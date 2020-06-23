import os
import secrets
import bson
import json
import pandas as pd
import numpy as np
# from scipy.stats import kruskal
import pingouin as pg
import pyexcel as p
from pingouin import kruskal
from surveyapp import dropzone, mongo
from flask import Flask, render_template, url_for, request, Blueprint, flash, redirect, current_app, abort, jsonify
from flask_login import login_required, current_user
from surveyapp.graphs.forms import UploadForm, EditForm, SaveGraphForm, StatisticalTestForm
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

@graphs.route('/input', methods=['GET', 'POST'])
@login_required
def input():
    survey_id = request.args.get("survey_id")
    data_obj = {}
    # The post method here is from the ajax call in the client javascript
    if request.method == "POST":
        # Get the survey ID from the client
        file_id = ObjectId(request.form["surveyId"])
        # Get the database object corresponding ton that ID
        file_obj = mongo.db.surveys.find_one_or_404({"_id":file_id})
        # Generate a random hex to be the new filename
        random_hex = secrets.token_hex(8)
        file_name = random_hex + ".csv"
        # Get the full path for saving the file
        file = os.path.join(current_app.root_path, "uploads", file_name)
        # Create and write the updated table to the file
        with open(file, "w") as new_file:
            new_file.write(request.form["table"])
        # Delete the old file
        old_file = os.path.join(current_app.root_path, "uploads", file_obj["fileName"])
        os.remove(old_file)
        # Update the database entry
        mongo.db.surveys.update_one({"_id": file_id},\
        {"$set": {"fileName" : file_name,\
                "user" : current_user._id,\
                "title" : file_obj["title"]}})
        flash("Data updated", "success")
        return redirect(url_for("graphs.home"))
    elif request.method == "GET" and survey_id:
        file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
        if file_obj["user"] != current_user._id:
            flash("You do not have access to that page", "error")
            return redirect(url_for("main.index"))
        df = read_from_file(file_obj["fileName"])
        data_obj = df.to_dict(orient="records")
    data = {"dataObj": data_obj, "surveyId": str(survey_id)}
    return render_template("input.html", title = "Input", data=data)





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


@graphs.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    surveys=mongo.db.surveys.find({"user":current_user._id})
    graphs=mongo.db.graphs.find({"user":current_user._id})
    tests=mongo.db.tests.find({"user":current_user._id})
    return render_template("home.html", title="Home", surveys=list(surveys), graphs=list(graphs), tests=list(tests))

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
# ALSO NEEDS REFACTORING AS GETTING QUITE LONG
@graphs.route('/barchart/<survey_id>', methods=['GET', 'POST'])
@login_required
def bar_chart(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    form = SaveGraphForm()
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))

    # This needs to be specified before 'form.validate_on_submit()' so Flask WTForms knows how to validate it
    df = read_from_file(file_obj["fileName"])
    column_info = parse_data(df)
    for column in column_info:
        form.x_axis.choices.append((column["title"], column["title"]))
        if column["data_type"] == "numerical":
            # We insert a tuple, The first is the 'value' of the select, the second is the text displayed
            form.y_axis.choices.append((column["title"], column["title"]))
    # Check to see if graph already exists
    graph_id = request.args.get("graph_id")
    # Now we have specified the 'select' options for the form, we can check 'form.validate_on_submit'
    if form.validate_on_submit():
        if form.x_axis.data == "Amount":
            y_agg = ""
        else:
            y_agg = form.y_axis_agg.data
        # setting upsert=true in the update will create the entry if it doesn't yet exist, else it updates
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)},\
        {"$set": {"title" : form.title.data,\
                "surveyId": survey_id,\
                "user" : current_user._id,\
                "xAxis" : form.x_axis.data,\
                "yAxis": form.y_axis.data,\
                "yAggregation": y_agg}}, upsert=True)
        return redirect(url_for("graphs.home", title="Home"))

    # If we are editing the graph instead of creating new, we want to prepopulate the fields
    graph_obj = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})
    if graph_obj:
        form.x_axis.data = graph_obj["xAxis"]
        form.y_axis.data = graph_obj["yAxis"]
        form.y_axis_agg.data = graph_obj["yAggregation"]
        form.title.data = graph_obj["title"]
    else:
        form.title.data = "Bar chart - " + file_obj["title"]

    # Converting the dataframe to a dict of records to be handled by D3.js on the client side.
    chart_data = df.to_dict(orient='records')
    data = {"chart_data": chart_data, "title": file_obj["title"], "column_info" : column_info}
    return render_template("barchart.html", title="Bar chart", data=data, form=form)




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
    return redirect(url_for('graphs.home'))


# EDIT A SURVEY
@graphs.route("/survey/<survey_id>/edit", methods=["GET", "POST"])
@login_required
def edit_survey(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        abort(403)
    form = EditForm()
    if form.validate_on_submit():
        mongo.db.surveys.update_one({"_id": file_obj["_id"]}, {"$set": {"title": form.title.data}})
        return redirect(url_for('graphs.home'))
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
    return redirect(url_for('graphs.home'))


# Analyse data sets
@graphs.route("/analyse", methods=['GET', 'POST'])
@login_required
def analyse():
    form = StatisticalTestForm()
    # Get a list of all surveys associate with the current user
    surveys = list(mongo.db.surveys.find({"user": current_user._id}))
    for survey in surveys:
        # Loop through each survey, saving the title (and filename) as well as the variables in the select options
        form.survey.choices.append((survey["_id"], survey["title"]))
        df = read_from_file(survey["fileName"])
        for variable in list(df.columns.values):
            form.independent_variable.choices.append((variable, variable))
            form.dependent_variable.choices.append((variable, variable))
    if form.validate_on_submit():
        # Get the dataset, and save the variables in python variables
        survey = mongo.db.surveys.find_one({"_id": form.survey.data})
        df = read_from_file(survey["fileName"])
        independent_variable = form.independent_variable.data
        dependent_variable = form.dependent_variable.data
        test = form.test.data
        if test == "Kruskall Wallis Test":
            kruskal_result = kruskal(data=df, dv=dependent_variable, between=independent_variable)
            p_value = kruskal_result["p-unc"][0]
        return redirect(url_for('graphs.result',\
                                survey=survey["_id"],\
                                test=test,\
                                p_value=p_value,\
                                independent_variable=independent_variable,\
                                dependent_variable=dependent_variable))
    return render_template("analysedata.html", form=form)



# Results from stats test
# IN THE FURUTRE, ADD FEATURE TO ADJUST THE P-VALUE????
@graphs.route("/result", methods=['GET', 'POST'])
@login_required
def result():
    form = EditForm()
    # Set a default alpha value 0.05 to compare the p value to
    alpha=0.05
    # cast string to float so it can be compared with the alpha value
    p_value=float(request.args.get("p_value"))
    test=request.args.get("test")
    independent_variable=request.args.get("independent_variable")
    dependent_variable=request.args.get("dependent_variable")
    # Get the survey variable so the test result can be saved and reference the survey
    survey=request.args.get("survey")
    test_id=request.args.get("test_id")
    if form.validate_on_submit():
        # 'upsert' creates entry if it does not yet exist
        mongo.db.tests.update_one({"_id": ObjectId(test_id)},\
        {"$set":{"survey" : survey,\
                "user" : current_user._id,\
                "title" : form.title.data,\
                "test" : test,\
                "independentVariable" : independent_variable,\
                "dependentVariable" : dependent_variable,\
                "p" : p_value}}, upsert=True)
        return redirect(url_for('graphs.home', title="Home"))
    title=request.args.get("title")
    if title:
        # i.e. if test already exists and user is clicking to view/edit it
        form.title.data = title
    else:
        # Set the default title. Users can change this
        form.title.data = independent_variable + "/" + dependent_variable + ": " + test
    result = {"test":test, "p":p_value, "alpha":alpha, "iv":independent_variable, "dv":dependent_variable}
    return render_template("result.html", result=result, form=form)



# DELETE A statistical test
@graphs.route("/analyse/<test_id>/delete", methods=['POST'])
@login_required
def delete_test(test_id):
    test_obj = mongo.db.tests.find_one_or_404({"_id":ObjectId(test_id)})
    if test_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        abort(403)
    mongo.db.tests.delete_one(test_obj)
    return redirect(url_for('graphs.home'))




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









# A 'helper' route that will return all the variables associated with a survey when called.
# Used by a javscript 'fetch' function for creating dynamic drop down boxes, with options changing based on previous options
@graphs.route("/analyse/<survey_id>")
def get_survey(survey_id):
    survey = mongo.db.surveys.find_one({"_id": ObjectId(survey_id)})
    df = read_from_file(survey["fileName"])
    column_info = parse_data(df)
    independent_variables = []
    dependent_variables = []
    for column in column_info:
        independent_variables.append(column["title"])
        if column["data_type"] == "numerical":
            dependent_variables.append(column["title"])
    return jsonify({"independentVariables" : independent_variables, "dependentVariables" : dependent_variables})
