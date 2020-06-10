import os
import secrets
import bson
import json
import pandas as pd
import numpy as np
from surveyapp import dropzone, mongo
from flask import Flask, render_template, url_for, request, Blueprint, flash, redirect, current_app
from flask_login import login_required, current_user
from surveyapp.graphs.forms import UploadForm
from bson.objectid import ObjectId


graphs = Blueprint("graphs", __name__)

# ------OLD CODE FOR DROPZONE------
# @graphs.route('/import', methods=['GET', 'POST'])
# # login required decorator prevents people accessing the page when not logged in
# @login_required
# def import_file():
#     if request.method == "POST":
#         f = request.files.get('file')
#         f.save(os.path.join('app/uploads', f.filename))
#     return render_template("import.html", title = "Import file")

# Function for saving file. Generates a random hex for the name
def save_file(form_file):
    random_hex = secrets.token_hex(8)
    # Split the extension from the fileName. I'm not using the filename so variable name is '_' according to PEP8
    _, f_ext = os.path.splitext(form_file.filename)
    file_name = random_hex + f_ext
    file_path = os.path.join(current_app.root_path, "uploads", file_name)
    form_file.save(file_path)
    return file_name

@graphs.route('/import', methods=['GET', 'POST'])
# login required decorator prevents people accessing the page when not logged in
@login_required
def import_file():
    form = UploadForm()
    # Checks validation when form is submitted with submit button
    if form.validate_on_submit():
        file_name = save_file(form.file.data)
        table = mongo.db.graphs.insert_one({\
        "fileName" : file_name,\
        "user" : current_user._id,\
        "title" : form.title.data})
        flash("File uploaded successfully!", "success")
        table_id = table.inserted_id
        return redirect(url_for("graphs.table", table_id=table_id))
    return render_template("import.html", title = "Import", form=form)


@graphs.route('/table/<table_id>', methods=['GET', 'POST'])
@login_required
def table(table_id):
    file_obj = mongo.db.graphs.find_one_or_404({"_id":ObjectId(table_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    df = read_from_file(file_obj["fileName"])

    # TO IMPLEMENT THIS WHEN DEALING WITH DATASETS THAT CONTAIN LEADING EMPTY ROWS/COLUMNS
    # data = remove_nan(df)
    # # set the 'header' to the first row in the table
    # new_header = data.iloc[0]
    # data = data[1:]
    # data.columns=new_header
    return render_template("table2.html", title="Table", data=df, table_title=file_obj["title"])
    # return render_template("table.html", title="Table", data=data)

# A function that removes all leading empty rows/columns
def remove_nan(df):
    data = df.dropna(how = 'all', axis = 1)
    data = data.dropna(how = 'all', axis = 0)
    print("FIRST ROW:")
    print (data.iloc[0][0])
    data = data.reset_index(drop = True)
    return data


@graphs.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    files=mongo.db.graphs.find({"user":current_user._id})
    return render_template("dashboard.html", title="Dashboard", files=list(files))

# RELOOK AT THIS. AT THE MOMENT I AM SENDING THE FILE ID BACK AND FORTH FROM THE SERVER. MIGHT BE BETTER TO USE LOCAL STORAGE??
@graphs.route('/choosegraph/<graph_id>', methods=['GET', 'POST'])
@login_required
def choose_graph(graph_id):
    file_obj = mongo.db.graphs.find_one_or_404({"_id":ObjectId(graph_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    df = read_from_file(file_obj["fileName"])
    return render_template("choosegraph.html", title="Select Graph", graph_id=file_obj["_id"], columns=list(df))

# RELOOK AT THIS. AT THE MOMENT I AM SENDING THE FILE ID BACK AND FORTH FROM THE SERVER. MIGHT BE BETTER TO USE LOCAL STORAGE??
@graphs.route('/barchart/<graph_id>', methods=['GET', 'POST'])
@login_required
def bar_chart(graph_id):
    file_obj = mongo.db.graphs.find_one_or_404({"_id":ObjectId(graph_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    df = read_from_file(file_obj["fileName"])
    # Parse the columns to get the type of data and number of unique entries.
    column_info = pase_data(df)
    column = request.args.get('column')
    # i.e. if it is categorical data...
    if df[column].dtypes == object:
        # ...then we want to aggregate it
        # df = df.groupby("Favourite ice-cream", as_index=False)["ID"].count()
        df = df.groupby(column)[column].agg("count").to_frame('c').reset_index()

    chart_data = df.to_dict(orient='records')
    # print(df.groupby("Favourite ice-cream").agg({"Favourite ice-cream": "count"}))
    # print(df)
    # chart_data = df.to_dict(orient='records')
    # chart_data = json.dumps(chart_data, indent=2)
    data = {"chart_data": chart_data, "chart_info": column_info, "title": file_obj["title"], "column" : column}
    return render_template("barchart.html", title="Bar chart", data=data, column=column)




# Reads the file (depending on type of file) and returns the dataframe
def read_from_file(filename):
    _, f_ext = os.path.splitext(filename)
    if f_ext == ".csv":
        data = pd.read_csv(os.path.join(current_app.root_path, "uploads", filename))
    else:
        data = pd.read_excel(os.path.join(current_app.root_path, "uploads", filename))
    return data



# This function loops through each column and collects information on the type of data (numerical vs categorical)
# and the number of unique entries in that column. The type of graph that can be used will depend on the type of data.
# Will also be useful for suggesting to the user about grouping if there are lots of unique entries.
# e.g. if there are 100 different 'ages', can suggest grouping in 10 year batches.
def pase_data(df):
    column_info = []
    for (column_title, column_data) in df.iteritems():
        if column_data.dtypes == object:
            data_type = "categorical"
        if column_data.dtypes == np.int64:
            data_type = "numerical"
        uniques = df[column_title].nunique()
        tempDict = {
        "title": column_title,
        "data_type": data_type,
        "num_unique": uniques
        }
        column_info.append(tempDict)
    return column_info
