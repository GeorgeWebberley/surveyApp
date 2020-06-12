import os
import pandas as pd
import numpy as np
from surveyapp import mongo
from flask import Flask, current_app
from flask_login import current_user
from bson.objectid import ObjectId

# Reads the file (depending on type of file) and returns the dataframe
def read_from_file(filename):
    _, f_ext = os.path.splitext(filename)
    if f_ext == ".csv":
        data = pd.read_csv(os.path.join(current_app.root_path, "uploads", filename))
    else:
        data = pd.read_excel(os.path.join(current_app.root_path, "uploads", filename))
    return data

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
        if column_data.dtypes == object:
            temp_dict["data_type"] = "categorical"
            temp_dict["num_unique"] = df[column_title].nunique()
            temp_dict["quantities"] = column_data.value_counts().to_dict()
        if column_data.dtypes == np.bool:
            temp_dict["data_type"] = "true/false"
            temp_dict["quantities"] = column_data.value_counts().to_dict()
        if column_data.dtypes == np.int64:
            temp_dict["data_type"] = "numerical"
            temp_dict["num_unique"] = df[column_title].nunique()
            temp_dict["average"] = column_data.agg("mean");
            temp_dict["max"] = column_data.agg("max");
            temp_dict["min"] = column_data.agg("min");
            temp_dict["sum"] = column_data.agg("sum");
        column_info.append(temp_dict)
    return column_info


# Saves new graph, else if already exists it updates the existing one
def save_graph(title, column, survey_id, graph_id):
    graph = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})
    if not graph:
        mongo.db.graphs.insert_one({\
        "title" : title,\
        "user" : current_user._id,\
        "column" : column,\
        "surveyId": survey_id})
    else:
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)}, {"$set": {"title": title}})
