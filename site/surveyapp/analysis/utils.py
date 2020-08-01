import pandas as pd
from surveyapp import mongo
# from flask import Flask, current_app
from bson.objectid import ObjectId
# For carrying out statistical test
from scipy.stats import chi2_contingency, chisquare
from pingouin import kruskal, mwu


# This is a function that will automatically run when the user uploads a file. It will parse the data and
# run some statistical tests based on the type of data in each column. It will not run all tests (for example,
# non-parametric tests will only be run on definite categorical data - i.e. data that is string, object or
# boolean. Ordinal data with numeric values, such as likert scale, will not be tested as this data will be
# identified as numeric.) Furthermore, the results of tests will have to be checked by the user, to check the
# data passes the assumptions of the test.
# Likewise, I do not perform mann whitney U and kruskal wallis on the same variables, even though it is in fact
# possible to perform kruskal wallis on 2 variables. This is to avoid conflicting results and subsequent increasing
# risk of false positives
def run_all_tests(survey_id, user_id, app):
    with app.app_context():
        run_tests(survey_id, user_id)

def run_tests(survey_id, user_id):
    file_obj = mongo.db.surveys.find_one({"_id":ObjectId(survey_id)})
    df = read_file(file_obj["fileName"])
    column_info = parse_data(df)
    test_results = []
    for column_1 in column_info:
        if column_1["data_type"] == "categorical" or column_1["data_type"] == "true/false":
            # Chi square goodness of fit only takes one, non-parametric variable
            p_value, result = chi_goodness(df, column_1["title"])
            if p_value < 0.05:
                test_results.append(result)
            # Now loop through again from the start, checking second variable against the first
            for column_2 in column_info:
                # If the columns are the same then we can contnue with next iteration
                if column_2["title"] == column_1["title"]:
                    continue
                elif column_2["data_type"] == "categorical" or column_2["data_type"] == "true/false":
                    # Chi square needs 2 categorical variables
                    p_value, result = chi_square(df, column_1["title"], column_2["title"])
                    # As Chi square can be done twice (with variable swapping places)
                    # we need to check that it has not yet been done
                    if p_value < 0.05 and not test_done(test_results, result):
                        test_results.append(result)
                elif column_2["data_type"] == "numerical":
                    if column_1["num_unique"] == 2 and column_2["num_unique"] > 1:
                        # We perform mann-whitney U test
                        p_value, result = mann_whitney(df, column_1["title"], column_2["title"])
                    elif column_1["num_unique"] > 2 and column_2["num_unique"] > 1:
                        # We perform kruskal wallis test
                        p_value, result = kruskal_wallis(df, column_1["title"], column_2["title"])
                    if p_value < 0.05:
                        test_results.append(result)
    # Now we can loop through the statistical tests, adding significant ones to
    # a temporary database. This will be presented to the user through a notficiation
    # on the home page.
    for result in test_results:
        mongo.db.temp_results.insert_one({
        "user": user_id,
        "survey_id" : survey_id,
        "result" : result})

# When adding chisquare test of independence, we need to check the test hasn't
# already been carried out (with the variables the opposite way round)
def test_done(previous_results, current_result):
    for result in previous_results:
        if current_result["variable_1"] == result["variable_2"] and current_result["variable_2"] == result["variable_1"]:
            return True
    return False


def kruskal_wallis(df, independent_variable, dependent_variable):
    kruskal_result = kruskal(data=df, dv=dependent_variable, between=independent_variable)
    # get the p-value (p-unc) from the kruskal test and convert to 4 decimal places only
    p_value = float("%.4f" % kruskal_result["p-unc"][0])
    # p_value = kruskal_result["p-unc"][0]
    result = {"test": "Kruskall Wallis Test",
            "p_value": p_value,
            "variable_1": independent_variable,
            "variable_2": dependent_variable,
            "null": f"The distribution of '{dependent_variable}' is the same across groups of '{independent_variable}'",
            "info": """Assumes that dependent variable ('{0}') is ordinal or continuous,
                    that the independent variable ('{1}') consists of more than 2 groups
                    and that these groups follow the same distribution (the shape on a histogram).\n
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
    keys = list(group_by.groups.keys())
    # Get the distinct keys (we have already checked there are only 2) and save them in variables
    group_1 = keys[0]
    group_2 = keys[1]
    # Perform test
    mwu_result = mwu(x, y)
    # Get the p_value from the result and format to 4 decimals
    p_value = float("%.4f" % mwu_result['p-val'].values[0])
    result = {"test": "Mann-Whitney U Test",
            "p_value": p_value,
            "variable_1": independent_variable,
            "variable_2": dependent_variable,
            "null": f"The distribution of '{dependent_variable}' is the same across groups of '{independent_variable}'",
            "info": """Assumes that the dependent variable ('{0}') is ordinal or continuous,
                    that the independent variable ('{1}') consists of just 2 groups
                    ('{2}' and '{3}') and that these groups follow the same distribution (the shape
                    on a histogram).""".format(dependent_variable, independent_variable, group_1, group_2)}
    return p_value, result



def chi_square(df, variable_1, variable_2):
    # 80% of groups must have a frequency of atleast 5.
    if not five_or_more(df, variable_1) or not five_or_more(df, variable_2):
         # If not, we can return 2, which is an impossible p-value and will be rejected.
        return 2, {}
    contingency_table = pd.crosstab(df[variable_1], df[variable_2])
    _, p_value, _, _ = chi2_contingency(contingency_table, correction=False)
    p_value = float("%.4f" % p_value)
    result = {"test": "Chi-Square test for independence",
            "p_value": p_value,
            "variable_1": variable_1,
            "variable_2": variable_2,
            "null": f"There is no relationship or association between '{variable_1}' and '{variable_2}'",
            "info": """Assumes that both variables are ordinal or nominal,
                    with each variable consisting of 2 or more groups. Also
                    assumes that 80% of the groups contain 5 or more counts."""}
    return p_value, result

# This checks if each category contains groups with at least a frequency of 5 in each group
# (e.g. If 'apple' is a result for 'favourite food' then this function checks if there are at at
# 5 responses with 'apple'). The chi-square independence test requires that 80% of groups contain
# a frequency of 5 or more.
def five_or_more(df, variable):
    group_by = df.groupby(variable)
    # We get the list of unique categories
    keys = list(group_by.groups.keys())
    count_over_5 = 0
    total_count = 0
    for key in keys:
        total_count += 1
        # Get the length (or count) of that category
        key_count = df[df[variable] == key].shape[0]
        if key_count >= 5:
            count_over_5 += 1
    if count_over_5/total_count < 0.8:
        return False
    else:
        return True



def chi_goodness(df, variable):
    # We first group the column by unique categories
    group_by = df.groupby(variable)
    # We get the list of unique categories
    keys = list(group_by.groups.keys())
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
        actual_distribution.append(key_count)
    # we will assume expected even distribution and only pass the actual distribution
    _, p_value = chisquare(actual_distribution)
    # Convert to 4 decimal places
    p_value = float("%.4f" % p_value)
    result = {"test": "Chi-Square goodness of fit",
            "p_value": p_value,
            "variable_1": variable,
            "variable_2": "",
            "null": f"Groups of '{variable}' are evenly distributed",
            "info": """Assumes that the expected distribution is even accross groups,
                    that each group is mutually exclusive from the next and each group
                    contains at least 5 subjects."""}
    return p_value, result
