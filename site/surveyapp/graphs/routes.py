import os
import secrets
import bson
import json
import pandas as pd
import numpy as np
from surveyapp import dropzone, mongo
from flask import Flask, render_template, url_for, request, Blueprint, flash, redirect, current_app, abort
from flask_login import login_required, current_user
from surveyapp.graphs.forms import UploadForm, EditSurveyForm, SaveGraphForm
from bson.objectid import ObjectId
from surveyapp.graphs.utils import parse_data, save_graph, read_from_file, remove_nan


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
        table = mongo.db.surveys.insert_one({\
        "fileName" : file_name,\
        "user" : current_user._id,\
        "title" : form.title.data})
        flash("File uploaded successfully!", "success")
        survey_id = table.inserted_id
        return redirect(url_for("graphs.table", survey_id=survey_id))
    return render_template("import.html", title = "Import", form=form)


@graphs.route('/table/<survey_id>', methods=['GET', 'POST'])
@login_required
def table(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
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
    return render_template("table2.html", title="Table", data=df, survey=file_obj)
    # return render_template("table.html", title="Table", data=data)


@graphs.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    surveys=mongo.db.surveys.find({"user":current_user._id})
    graphs=mongo.db.graphs.find({"user":current_user._id})
    return render_template("dashboard.html", title="Dashboard", surveys=list(surveys), graphs=list(graphs))

# RELOOK AT THIS. AT THE MOMENT I AM SENDING THE FILE ID BACK AND FORTH FROM THE SERVER. MIGHT BE BETTER TO USE LOCAL STORAGE??
@graphs.route('/choosegraph/<survey_id>', methods=['GET', 'POST'])
@login_required
def choose_graph(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    df = read_from_file(file_obj["fileName"])
    return render_template("choosegraph.html", title="Select Graph", survey_id=file_obj["_id"], columns=list(df))

# RELOOK AT THIS. AT THE MOMENT I AM SENDING THE FILE ID BACK AND FORTH FROM THE SERVER. MIGHT BE BETTER TO USE LOCAL STORAGE??
@graphs.route('/barchart/<survey_id>', methods=['GET', 'POST'])
@login_required
def bar_chart(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    form = SaveGraphForm()
    column = request.args.get('column')
    graph_id = request.args.get('graph_id')
    if form.validate_on_submit():
        save_graph(form.title.data, column, survey_id, graph_id);
        return redirect(url_for("graphs.dashboard"))
    elif request.method == "GET":
        df = read_from_file(file_obj["fileName"])
        # column_info = pase_data(df)
        df = df.groupby(column)[column].agg("count")
        df = df.to_frame('c').reset_index()
        # Converting the dataframe to a dict of records to be handled by D3.js on the client side.
        chart_data = df.to_dict(orient='records')
        data = {"chart_data": chart_data, "title": file_obj["title"], "column" : column}
        if request.args.get('title') == None:
            form.title.data = "Bar chart - " + file_obj["title"] + ": " + column
        else:
            form.title.data = request.args.get('title')
    return render_template("barchart.html", title="Bar chart", data=data, column=column, form=form)

# RELOOK AT THIS. AT THE MOMENT I AM SENDING THE FILE ID BACK AND FORTH FROM THE SERVER. MIGHT BE BETTER TO USE LOCAL STORAGE??
@graphs.route('/barchart2/<survey_id>', methods=['GET'])
@login_required
def bar_chart2(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))

    df = read_from_file(file_obj["fileName"])
    column_info = parse_data(df)
    # Converting the dataframe to a dict of records to be handled by D3.js on the client side.
    chart_data = df.to_dict(orient='records')
    data = {"chart_data": chart_data, "title": file_obj["title"], "column_info" : column_info}

    return render_template("barchart2.html", title="Bar chart", data=data)







# DELETE A SURVEY
# NEED TO ADD FEATURE SO FILE IS REMOVED AND ALSO THAT ALL GRAPHS ARE REMOVED RELATING TO THE FILE
@graphs.route("/survey/<survey_id>/delete", methods=['POST'])
@login_required
def delete_survey(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        abort(403)
    graphs = mongo.db.graphs.find({"surveyId":survey_id})
    # print(graphs)
    for graph in graphs:
        mongo.db.graphs.delete_one(graph)
    mongo.db.surveys.delete_one(file_obj)
    return redirect(url_for('graphs.dashboard'))


# EDIT A SURVEY
@graphs.route("/survey/<survey_id>/edit", methods=["GET", "POST"])
@login_required
def edit_survey(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        abort(403)
    form = EditSurveyForm()
    if form.validate_on_submit():
        mongo.db.surveys.update_one({"_id": file_obj["_id"]}, {"$set": {"title": form.title.data}})
        return redirect(url_for('graphs.dashboard'))
    elif request.method == "GET":
        form.title.data = file_obj["title"]
        # form.process()
    return render_template("edit_survey.html", form=form)


# DELETE A Graph
@graphs.route("/graph/<graph_id>/delete", methods=['POST'])
@login_required
def delete_graph(graph_id):
    graph_obj = mongo.db.graphs.find_one_or_404({"_id":ObjectId(graph_id)})
    if graph_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        abort(403)
    mongo.db.graphs.delete_one(graph_obj)
    return redirect(url_for('graphs.dashboard'))


# Analyse data sets
@graphs.route("/analyse", methods=['GET'])
@login_required
def analyse():
    surveys = mongo.db.surveys.find({"user": current_user._id})
    return render_template("analysedata.html", surveys=surveys)


# Give the user a quick overview of stats on the survey data
@graphs.route("/quickstats/<survey_id>", methods=['GET'])
@login_required
def quick_stats(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    df = read_from_file(file_obj["fileName"])
    rows = len(df.index)
    cols = len(df.columns)
    column_info = parse_data(df);
    return render_template("quickstats.html", rows=rows, cols=cols, column_info=column_info )
