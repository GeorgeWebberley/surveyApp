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
    print("FIRST ROW:")
    print (data.iloc[0][0])
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
        print("Title:")
        print(column_title)
        print("Type:")
        print(column_data.dtypes)
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
            # Try to parse it as a date/time. If it fails, it must be an object (categorical data)
            try:
                df[column_title] = pd.to_datetime(df[column_title], dayfirst=True, errors='coerce')
                # df[column_title].dt.to_pydatetime()
                if (df[column_title].dt.floor('d') == df[column_title]).all():
                    temp_dict["data_type"] = "date"
                elif (df[column_title].dt.date == pd.Timestamp('now').date()).all():
                    df[column_title] = df[column_title].dt.time
                    temp_dict["data_type"] = "time"
                else:
                    temp_dict["data_type"] = "date/time"

                # print("BEFORE:")
                # print(column_data)
                # df[column_title] = pd.to_datetime(column_data, dayfirst=True)
                # column_data = pd.to_datetime(column_data, dayfirst=True)
                # print("AFTER:")
                # print(column_data)
                # temp_dict["data_type"] = "date/time"
                temp_dict["num_unique"] = df[column_title].nunique()
            except ValueError:
                temp_dict["data_type"] = "categorical"
                temp_dict["num_unique"] = df[column_title].nunique()
                temp_dict["quantities"] = column_data.value_counts().to_dict()
        column_info.append(temp_dict)
    return column_info, df


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
