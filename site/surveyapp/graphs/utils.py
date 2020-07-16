import os
import secrets
import pandas as pd

import numpy as np
from surveyapp import mongo
from flask import Flask, current_app
from flask_login import current_user
from bson.objectid import ObjectId
# For converting image base 64 data URI
import urllib.parse
# For carrying out statistical test
from scipy.stats import chi2_contingency, chisquare
import pingouin as pg
from pingouin import kruskal, mwu


# Saves file after import. All files are saved as CSV for easier handling
def save_file(form_file):
    # Generate a random hex for the filename
    random_hex = secrets.token_hex(8)
    file_name = random_hex + ".csv"
    file_path = os.path.join(current_app.root_path, "uploads", file_name)
    # Split the extension from the fileName. I'm not using the filename so variable name is '_' according to PEP8
    _, f_ext = os.path.splitext(form_file.filename)
    # If not CSV file I will convert it to csv before saving (for easier handling later)
    if f_ext != ".csv":
        data_xls = pd.read_excel(form_file, index_col=None)
        data_xls.to_csv(file_path, encoding='utf-8', index=False)
    else:
        form_file.save(file_path)
    return file_name

# Given a name, locates file and returns the dataframe.
def read_file(name):
    return pd.read_csv(os.path.join(current_app.root_path, "uploads", name))


def save_image(data, graph_id):
    graph = mongo.db.graphs.find_one({"_id": ObjectId(graph_id)})
    if graph:
        delete_image(graph["image"])
    response = urllib.request.urlopen(data)
    # generate a random hex for the filename
    random_hex = secrets.token_hex(8)
    file_name = random_hex + ".png"
    file = os.path.join(current_app.root_path, "static/graphimages", file_name)
    with open(file, 'wb') as image_to_write:
        image_to_write.write(response.file.read())
    return file_name

def delete_image(name):
    image = os.path.join(current_app.root_path, "static/graphimages", name)
    os.remove(image)

def delete_file(name):
    file = os.path.join(current_app.root_path, "uploads", name)
    os.remove(file)


# A function that removes all leading empty rows/columns
def remove_nan(df):
    data = df.dropna(how = 'all', axis = 1)
    data = data.dropna(how = 'all', axis = 0)
    data = data.reset_index(drop = True)
    return data

# This function loops through each column and collects information on the type of data (numerical vs categorical)
# and the number of unique entries in that column. The type of graph that can be used will depend on the type of data.
# Will also be useful for suggesting to the user about grouping if there are lots of unique entries.
# e.g. if there are 100 different 'ages', can suggest grouping in 10 year batches.
def parse_data(df):
    column_info = []
    for (column_title, column_data) in df.iteritems():
        uniques = df[column_title].nunique()
        temp_dict = {
        "title": column_title
        }
        if column_data.dtypes == np.bool:
            temp_dict["data_type"] = "true/false"
            temp_dict["quantities"] = column_data.value_counts().to_dict()
        elif column_data.dtypes == np.int64:
            temp_dict["data_type"] = "numerical"
            temp_dict["num_unique"] = df[column_title].nunique()
            temp_dict["average"] = column_data.agg("mean");
            temp_dict["max"] = column_data.agg("max");
            temp_dict["min"] = column_data.agg("min");
            temp_dict["sum"] = column_data.agg("sum");
        else:
            temp_dict["data_type"] = "categorical"
            temp_dict["num_unique"] = df[column_title].nunique()
            temp_dict["quantities"] = column_data.value_counts().to_dict()
            # # Try to parse it as a date/time. If it fails, it must be an object (categorical data)
            # try:
            #     column_data = pd.to_datetime(column_data, dayfirst=True, errors='coerce')
            #     if (column_data.dt.floor('d') == column_data).all():
            #         temp_dict["data_type"] = "date"
            #     elif (column_data.dt.date == pd.Timestamp('now').date()).all():
            #         column_data = column_data.dt.time
            #         temp_dict["data_type"] = "time"
            #     else:
            #         temp_dict["data_type"] = "date/time"
            #     temp_dict["num_unique"] = df[column_title].nunique()
            # except ValueError:
            #     temp_dict["data_type"] = "categorical"
            #     temp_dict["num_unique"] = df[column_title].nunique()
            #     temp_dict["quantities"] = column_data.value_counts().to_dict()
        column_info.append(temp_dict)
    return column_info


# Saves new graph, else if already exists it updates the existing one
def save_graph(title, survey_id, graph_id, x_variable, y_variable, y_aggregation):
    graph = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})
    if not graph:
        mongo.db.graphs.insert_one({\
        "title" : title,\
        "user" : current_user._id,\
        "column" : column,\
        "surveyId": survey_id})
    else:
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)}, {"$set": {"title": title}})


# This is a function that will automatically run when the user uploads a file. It will parse the data and
# run some statistical tests based on the type of data in each column. It will not run all tests (for example,
# non-parametric tests will only be run on definite categorical data - i.e. data that is string, object or
# boolean. Ordinal data with numeric values, such as likert scale, will not be tested as this data will be
# identified as numeric.) Furthermore, the results of tests will have to be checked by the user, to check the
# data passes the assumptions of the test.
# Likewise, I do not perform mann whitney U and kruskal wallis on the same variables, even though it is in fact
# possible to perform kruskal wallis on 2 variables. This is to avoid conflicting results and subsequent increasing
# risk of false positives
def run_all_tests(survey_id):
    file_obj = mongo.db.surveys.find_one({"_id":ObjectId(survey_id)})
    df = read_file(file_obj["fileName"])
    column_info = parse_data(df)
    test_results = []
    for column_1 in column_info:
        print("test")
        print(column_1)
        if column_1["data_type"] == "categorical" or column_1["data_type"] == "true/false":
            print("test3")
            # Chi square goodness of fit only takes one variable non-parametric
            p_value, result = chi_goodness(df, column_1["title"])
            print("p-value:")
            print(p_value)
            if p_value < 0.05:
                test_results.append(result)
            for column_2 in column_info:
                print("test2")
                if column_2["title"] == column_1["title"]:
                    continue
                if column_2["data_type"] == "categorical" or column_2["data_type"] == "true/false":
                    # Chi square needs 2 categorical variables
                    p_value, result = chi_square(df, column_1["title"], column_2["title"])
                    print("p-value:")
                    print(p_value)
                    if p_value < 0.05:
                        test_results.append(result)

                if column_2["data_type"] == "numerical":
                    if column_1["num_unique"] == 2:
                        # We perform mann-whitney U test
                        p_value, result = mann_whitney(df, column_1["title"], column_2["title"])

                    elif column_1["num_unique"] > 2:
                        # We perform kruskal wallis test
                        p_value, result = kruskal_wallis(df, column_1["title"], column_2["title"])
                print("p-value:")
                print(p_value)
                if p_value < 0.05:
                    test_results.append(result)
    return test_results


def kruskal_wallis(df, independent_variable, dependent_variable):
    kruskal_result = kruskal(data=df, dv=dependent_variable, between=independent_variable)
    # get the p-value (p-unc) from the kruskal test and convert to 4 decimal places only
    p_value = kruskal_result["p-unc"][0]
    # p_value = "%.4f" % kruskal_result["p-unc"][0]
    result = {"test": "Kruskall Wallis Test",
            "p_value": p_value,
            "null": f"The distribution of {dependent_variable} is the same across groups of {independent_variable}",
            "info": """Assumes that dependent variable ({0}) is ordinal or continuous,
                    that the independent variable ({1}) consists of more than 2 groups
                    and that these groups follow the same distribution (the shape on a histogram)
                    NOTE: It is also possible to perform this test on categories containing just 2 groups,
                    however we have not done so as it could conflict with results from Mann-Whitney U test
                    (performed on categories with 2 groups only).""".format(dependent_variable, independent_variable)}
    return p_value, result


def mann_whitney(df, independent_variable, dependent_variable):
    # Group the data by the independent_variable
    group_by = df.groupby(independent_variable)
    # Convert to an array of groups
    group_array = [group_by.get_group(x) for x in group_by.groups]
    # Get the values of groups 1 and 2 from the array
    x = group_array[0][dependent_variable].values
    y = group_array[1][dependent_variable].values
    # Perform test
    mwu_result = mwu(x, y)
    # Get the p_value from the result and format to 4 decimals
    # p_value = "%.4f" % mwu_result['p-val'].values[0]
    p_value = mwu_result['p-val'].values[0]
    result = {"test": "Mann-Whitney U Test",
            "p_value": p_value,
            "null": f"The distribution of {dependent_variable} is the same across groups of {independent_variable}",
            "info": """Assumes that dependent variable ({0}) is ordinal or continuous,
                    that the independent variable ({1}) consists of just 2 groups
                    ({2} and {3}) and that these groups follow the same distribution (the shape
                    on a histogram).""".format(dependent_variable, independent_variable, x, y)}
    return p_value, result



def chi_square(df, variable_1, variable_2):
    contingency_table = pd.crosstab(df[variable_1], df[variable_2])
    _, p_value, _, _ = chi2_contingency(contingency_table, correction=False)
    result = {"test": "Chi-Square test for independence",
            "p_value": p_value,
            "null": f"There is no relationship or association between {variable_1} and {variable_2}",
            "info": """Assumes that both variables are ordinal or nominal,
                    with each variable consisting of 2 or more groups."""}
    return p_value, result


def chi_goodness(df, variable):
    # We first group the column by unique categories
    group_by = df.groupby(variable)
    # We get the list of unique categories
    keys = list(group_by.groups.keys())
    # We get the total count of rows/subjects
    total_count = len(df.index)
    actual_distribution = []
    # Loop through each unique category
    for key in keys:
        # Get the length (or count) of that category
        key_count = df[df[variable] == key].shape[0]
        if key_count <= 5:
            # Each group must have a frequency of atleast 5. If not, we can return 2,
            # which is an impossible p-value and will be rejected.
            return 2, {}
        # And add it to our list
        actual_distribution.append((key_count*100)/total_count)
    # we will assume expected even distribution and only pass the actual distribution
    _, p_value = chisquare(actual_distribution)
    result = {"test": "Chi-Square goodness of fit",
            "p_value": p_value,
            "null": f"Groups of {variable} are evenly distributed",
            "info": """Assumes that the expected distribution is even accross groups,
                    that each group is mutually exclusive from the next and each group
                    contains at least 5 subjects."""}
    return p_value, result
