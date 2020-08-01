import os
import secrets
import pandas as pd

import numpy as np
from flask import Flask, current_app


# Saves file after import. All files are saved as CSV for easier handling
def save_file(form_file):
    # Split the extension from the fileName. I'm not using the filename so variable name is '_' according to PEP8
    _, f_ext = os.path.splitext(form_file.filename)
    # If not CSV file I will convert it to csv before saving (for easier handling later)
    if f_ext != ".csv":
        df = pd.read_excel(form_file, index_col=None)
    else:
        df = pd.read_csv(form_file, index_col=None)
    # Removes empty rows/columns
    df = remove_nan(df)
    # Trims white space from strings
    df = trim_strings(df)
    # Generate a random hex filename and create the path
    file_name = generate_filepath()
    file_path = os.path.join(current_app.root_path, "uploads", file_name)
    # Save as CSV
    df.to_csv(file_path, encoding='utf-8', index=False)
    return file_name

# Uses python secrets to generate a random hex token for the file name
def generate_filepath():
    # Generate a random hex for the filename
    random_hex = secrets.token_hex(8)
    file_name = random_hex + ".csv"
    return file_name



def trim_strings(df):
    trimmed = lambda x: x.strip() if isinstance(x, str) else x
    return df.applymap(trimmed)


# Given a name, locates file and returns the dataframe.
def read_file(name):
    return pd.read_csv(os.path.join(current_app.root_path, "uploads", name))


def delete_file(name):
    file = os.path.join(current_app.root_path, "uploads", name)
    os.remove(file)


# A function that removes all leading empty rows/columns
def remove_nan(df):
    # Set a flag that is true if the first row is empty (subsequenlty requiring
    # the header be reset after empty rows are removed)
    if df.iloc[0].isnull().all(axis = 0):
        reset_header = True
    else:
        reset_header = False
    # Drops columns
    data = df.dropna(how = 'all', axis = 1)
    # Drops rows
    data = data.dropna(how = 'all', axis = 0)
    data = data.reset_index(drop = True)
    # if the first row was empty, we reset the header to be the first row in the data
    if reset_header:
        # Get the first row to be set as the new header
        new_header = data.iloc[0]
        # Set the remaining data as the dataframe
        data = data[1:]
        # Set the new header on the dataframe
        data.columns = new_header
    return data

# This function loops through each column and collects information on the type of data (numerical vs categorical)
# and the number of unique entries in that column. The type of graph that can be used will depend on the type of data.
# Will also be useful for suggesting to the user about grouping if there are lots of unique entries.
# e.g. if there are 100 different 'ages', can suggest grouping in 10 year batches.
def parse_data(df):
    numerics = [np.int64, np.int32, np.int16, np.int8, np.float64, np.float32, np.float16, np.uint64, np.uint32, np.uint16, np.uint8]
    column_info = []

    for (column_title, column_data) in df.iteritems():
        uniques = df[column_title].nunique()
        temp_dict = {
        "title": column_title
        }
        temp_dict["num_unique"] = df[column_title].nunique()
        if column_data.dtype == np.bool:
            temp_dict["data_type"] = "true/false"
            temp_dict["quantities"] = column_data.value_counts().to_dict()
        elif column_data.dtype in numerics:
            temp_dict["data_type"] = "numerical"
            # Rounded to 4 significant figures so that it can fit on the page
            temp_dict["standard_deviation"] = float('%.4g' % column_data.std())
            temp_dict["average"] = float('%.4g' % column_data.agg("mean"))
            temp_dict["max"] = column_data.agg("max");
            temp_dict["min"] = column_data.agg("min");
            temp_dict["sum"] = column_data.agg("sum");
        else:
            # Try to parse it as a date/time. If it fails, it must be an object (categorical data)
            try:
                column_data = pd.to_datetime(column_data, dayfirst=True)
                if (column_data.dt.floor('d') == column_data).all():
                    temp_dict["data_type"] = "date"
                elif (column_data.dt.date == pd.Timestamp('now').date()).all():
                    column_data = column_data.dt.time
                    temp_dict["data_type"] = "time"
                else:
                    temp_dict["data_type"] = "date/time"
                temp_dict["num_unique"] = df[column_title].nunique()
            except ValueError:
                temp_dict["data_type"] = "categorical"
                temp_dict["quantities"] = column_data.value_counts().to_dict()
        column_info.append(temp_dict)
    return column_info
