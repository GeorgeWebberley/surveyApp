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
from surveyapp.graphs.forms import UploadForm, EditForm, BarchartForm, ScatterchartForm, StatisticalTestForm
from bson.objectid import ObjectId
from bson.json_util import loads, dumps
from surveyapp.graphs.utils import parse_data, save_graph, save_file, remove_nan
# For converting image base 64 data URI
from binascii import a2b_base64
import urllib.parse



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
    # Initialise variables (values for data, headers for column headers)
    value_list = []
    header_list = []
    survey_id = request.args.get("survey_id")
    form = EditForm()
    # Handsontable data cannot be posted using normal WTForms methods.
    # This post method is from an AJAX call in the client javascript.
    if form.validate_on_submit():
        # get the file_obj (if one exists yet)
        file_obj = mongo.db.surveys.find_one({"_id":ObjectId(survey_id)})
        # if file already exists we can simply get the name of the file
        if file_obj:
            file_name = file_obj["fileName"]
            file = os.path.join(current_app.root_path, "uploads", file_name)
        # Else we need to generate a new filename with a new random hex.
        else:
            # Generate a random hex to be the new filename
            random_hex = secrets.token_hex(8)
            file_name = random_hex + ".csv"
            file = os.path.join(current_app.root_path, "uploads", file_name)
        # write/overwrite the table values to the file
        with open(file, "w") as file_to_write:
            file_to_write.write(request.form["table"])
        # Update/insert into the database
        mongo.db.surveys.update_one({"_id": ObjectId(survey_id)},\
        {"$set": {"fileName" : file_name,\
                "user" : current_user._id,\
                "title" : form.title.data}}, upsert=True)
    # If GET request and the survey already exists (i.e. editing an existing survey)
    elif request.method == "GET" and survey_id:
        file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
        if file_obj["user"] != current_user._id:
            flash("You do not have access to that page", "error")
            return redirect(url_for("main.index"))
        # Read the file and extract the cell values and column headers
        df = pd.read_csv(os.path.join(current_app.root_path, "uploads", file_obj["fileName"]))
        value_list = df.values.tolist()
        header_list = df.columns.values.tolist()
        form.title.data = file_obj["title"]
    data = {"values": value_list, "headers": header_list}
    return render_template("input.html", title = "Input", data=data, survey_id=survey_id, form=form)



@graphs.route('/table/<survey_id>', methods=['GET', 'POST'])
@login_required
def table(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    df = pd.read_csv(os.path.join(current_app.root_path, "uploads", file_obj["fileName"]))
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
    return render_template("home.html", title="Home", surveys=list(surveys))


@graphs.route('/home/<survey_id>', methods=['GET', 'POST'])
@login_required
def dashboard(survey_id):
    survey = mongo.db.surveys.find_one_or_404({"_id": ObjectId(survey_id)})
    graphs = mongo.db.graphs.find({"surveyId":survey_id})
    tests = mongo.db.tests.find({"surveyId":survey_id})
    # return render_template("home.html", title="Home", surveys=list(surveys), graphs=list(graphs), tests=list(tests))
    return render_template("dashboard.html", title="Dashboard", graphs=list(graphs), tests=list(tests), survey=survey)






# RELOOK AT THIS. AT THE MOMENT I AM SENDING THE FILE ID BACK AND FORTH FROM THE SERVER. MIGHT BE BETTER TO USE LOCAL STORAGE??
@graphs.route('/choosegraph/<survey_id>', methods=['GET', 'POST'])
@login_required
def choose_graph(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    df = pd.read_csv(os.path.join(current_app.root_path, "uploads", file_obj["fileName"]))
    return render_template("choosegraph.html", title="Select Graph", survey_id=file_obj["_id"], columns=list(df))


# RELOOK AT THIS. AT THE MOMENT I AM SENDING THE FILE ID BACK AND FORTH FROM THE SERVER. MIGHT BE BETTER TO USE LOCAL STORAGE??
# ALSO NEEDS REFACTORING AS GETTING QUITE LONG
@graphs.route('/barchart/<survey_id>', methods=['GET', 'POST'])
@login_required
def bar_chart(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    form = BarchartForm()
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    # This needs to be specified before 'form.validate_on_submit()' so Flask WTForms knows how to validate it
    df = pd.read_csv(os.path.join(current_app.root_path, "uploads", file_obj["fileName"]))
    column_info = parse_data(df)
    for column in column_info:
        form.x_axis.choices.append((column["title"], column["title"]))
        if column["data_type"] == "numerical":
            # We insert a tuple, The first is the 'value' of the select, the second is the text displayed
            form.y_axis.choices.append((column["title"], column["title"]))
    # Get the ID of the graph (if it exists yet)
    graph_id = request.args.get("graph_id")
    # Now we have specified the 'select' options for the form, we can check 'form.validate_on_submit'
    if form.validate_on_submit():
        imageData = request.form["image"]
        response = urllib.request.urlopen(imageData)
        # generate a random hex for the filename
        random_hex = secrets.token_hex(8)
        file_name = random_hex + ".png"
        file = os.path.join(current_app.root_path, "static/graphimages", file_name)
        with open(file, 'wb') as image_to_write:
            image_to_write.write(response.file.read())
        if form.x_axis.data == "Amount":
            y_agg = ""
        else:
            y_agg = form.y_axis_agg.data
        # setting upsert=true in the update will create the entry if it doesn't yet exist, else it updates
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)},\
        {"$set": {"title" : form.title.data,\
                "surveyId": survey_id,\
                "user" : current_user._id,\
                "type" : "Bar chart",\
                "xAxis" : form.x_axis.data,\
                "yAxis": form.y_axis.data,\
                "yAggregation": y_agg,
                "image": file_name}}, upsert=True)
        return redirect(url_for("graphs.dashboard", title="Dashboard", survey_id=survey_id))
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
    return render_template("barchart.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id)


@graphs.route('/scatterchart/<survey_id>', methods=['GET', 'POST'])
@login_required
def scatter_chart(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    form = ScatterchartForm()
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    # This needs to be specified before 'form.validate_on_submit()' so Flask WTForms knows how to validate it
    df = pd.read_csv(os.path.join(current_app.root_path, "uploads", file_obj["fileName"]))
    column_info = parse_data(df)
    for column in column_info:
        # Scatter charts require both x and y axis to have some numerical value (i.e. ordinal/interval but not categorical)
        if column["data_type"] == "numerical":
            # We insert a tuple, The first is the 'value' of the select, the second is the text displayed
            form.x_axis.choices.append((column["title"], column["title"]))
            form.y_axis.choices.append((column["title"], column["title"]))
    # Get the id of the graph (if it exists yet)
    graph_id = request.args.get("graph_id")
    # Now we have specified the 'select' options for the form, we can check 'form.validate_on_submit'
    if form.validate_on_submit():
        imageData = request.form["image"]
        response = urllib.request.urlopen(imageData)
        # generate a random hex for the filename
        random_hex = secrets.token_hex(8)
        file_name = random_hex + ".png"
        file = os.path.join(current_app.root_path, "static/graphimages", file_name)
        with open(file, 'wb') as image_to_write:
            image_to_write.write(response.file.read())
        # setting upsert=true in the update will create the entry if it doesn't yet exist, else it updates
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)},\
        {"$set": {"title" : form.title.data,\
                "surveyId": survey_id,\
                "user" : current_user._id,\
                "type" : "Scatter chart",\
                "xAxis" : form.x_axis.data,\
                "yAxis": form.y_axis.data,\
                "image": file_name}}, upsert=True)
        return redirect(url_for("graphs.dashboard", title="Dashboard", survey_id=survey_id))
    graph_id = request.args.get("graph_id")
    # If we are editing the graph instead of creating new, we want to prepopulate the fields
    graph_obj = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})
    if graph_obj:
        form.x_axis.data = graph_obj["xAxis"]
        form.y_axis.data = graph_obj["yAxis"]
        form.title.data = graph_obj["title"]
    else:
        form.title.data = "Scatter chart - " + file_obj["title"]
    # Converting the dataframe to a dict of records to be handled by D3.js on the client side.
    chart_data = df.to_dict(orient='records')
    data = {"chart_data": chart_data, "title": file_obj["title"], "column_info" : column_info}
    return render_template("scatterchart.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id)






@graphs.route('/graph/<survey_id>', methods=['GET', 'POST'])
@login_required
def graph(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    chart_type = request.args.get("chart_type")
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        return redirect(url_for("main.index"))
    # Get the id of the graph (if it exists yet)
    graph_id = request.args.get("graph_id")
    # Read the csv file in
    df = pd.read_csv(os.path.join(current_app.root_path, "uploads", file_obj["fileName"]))
    # Converting the dataframe to a dict of records to be handled by D3.js on the client side.
    chart_data = df.to_dict(orient='records')
    # parse the columns to get information regarding type of data
    column_info = parse_data(df)

    print("Chart_type")
    print(chart_type)



    # ----------BAR CHART----------
    if chart_type == "Bar chart":
        return bar_chart(survey_id, column_info, chart_data, df, graph_id, file_obj["title"])

    # ----------SCATTER CHART----------
    elif chart_type == "Scatter chart":
        return scatter_chart(survey_id, column_info, chart_data, df, graph_id, file_obj["title"])




def bar_chart(survey_id, column_info, chart_data, df, graph_id, title):
    form = BarchartForm()
    for column in column_info:
        form.x_axis.choices.append((column["title"], column["title"]))
        if column["data_type"] == "numerical":
            # We insert a tuple, The first is the 'value' of the select, the second is the text displayed
            form.y_axis.choices.append((column["title"], column["title"]))
    # Now we have specified the 'select' options for the form, we can check 'form.validate_on_submit'
    if form.validate_on_submit():
        imageData = request.form["image"]
        response = urllib.request.urlopen(imageData)
        # generate a random hex for the filename
        random_hex = secrets.token_hex(8)
        file_name = random_hex + ".png"
        file = os.path.join(current_app.root_path, "static/graphimages", file_name)
        with open(file, 'wb') as image_to_write:
            image_to_write.write(response.file.read())
        if form.x_axis.data == "Amount":
            y_agg = ""
        else:
            y_agg = form.y_axis_agg.data
        # setting upsert=true in the update will create the entry if it doesn't yet exist, else it updates
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)},\
        {"$set": {"title" : form.title.data,\
                "surveyId": survey_id,\
                "user" : current_user._id,\
                "type" : "Bar chart",\
                "xAxis" : form.x_axis.data,\
                "yAxis": form.y_axis.data,\
                "yAggregation": y_agg,
                "image": file_name}}, upsert=True)
        return redirect(url_for("graphs.dashboard", title="Dashboard", survey_id=survey_id))

    # If we are editing the graph instead of creating new, we want to prepopulate the fields
    graph_obj = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})

    if graph_obj:
        form.x_axis.data = graph_obj["xAxis"]
        form.y_axis.data = graph_obj["yAxis"]
        form.y_axis_agg.data = graph_obj["yAggregation"]
        form.title.data = graph_obj["title"]
    else:
        form.title.data = "Bar chart - " + title

    data = {"chart_data": chart_data, "title": title, "column_info" : column_info}
    return render_template("barchart.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id)


def scatter_chart(survey_id, column_info, chart_data, df, graph_id, title):
    form = ScatterchartForm()
    for column in column_info:
        # Scatter charts require both x and y axis to have some numerical value (i.e. ordinal/interval but not categorical)
        if column["data_type"] == "numerical":
            # We insert a tuple, The first is the 'value' of the select, the second is the text displayed
            form.x_axis.choices.append((column["title"], column["title"]))
            form.y_axis.choices.append((column["title"], column["title"]))
    # Now we have specified the 'select' options for the form, we can check 'form.validate_on_submit'
    if form.validate_on_submit():
        imageData = request.form["image"]
        response = urllib.request.urlopen(imageData)
        # generate a random hex for the filename
        random_hex = secrets.token_hex(8)
        file_name = random_hex + ".png"
        file = os.path.join(current_app.root_path, "static/graphimages", file_name)
        with open(file, 'wb') as image_to_write:
            image_to_write.write(response.file.read())
        # setting upsert=true in the update will create the entry if it doesn't yet exist, else it updates
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)},\
        {"$set": {"title" : form.title.data,\
                "surveyId": survey_id,\
                "user" : current_user._id,\
                "type" : "Scatter chart",\
                "xAxis" : form.x_axis.data,\
                "yAxis": form.y_axis.data,\
                "image": file_name}}, upsert=True)
        return redirect(url_for("graphs.dashboard", title="Dashboard", survey_id=survey_id))

    # If we are editing the graph instead of creating new, we want to prepopulate the fields
    graph_obj = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})

    if graph_obj:
        form.x_axis.data = graph_obj["xAxis"]
        form.y_axis.data = graph_obj["yAxis"]
        form.title.data = graph_obj["title"]
    else:
        form.title.data = "Scatter chart - " + title

    data = {"chart_data": chart_data, "title": title, "column_info" : column_info}
    return render_template("scatterchart.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id)













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
@graphs.route("/home/<survey_id>/<graph_id>/delete", methods=['POST'])
@login_required
def delete_graph(graph_id, survey_id):
    graph_obj = mongo.db.graphs.find_one_or_404({"_id":ObjectId(graph_id)})
    if graph_obj["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        abort(403)
    mongo.db.graphs.delete_one(graph_obj)
    return redirect(url_for('graphs.dashboard', survey_id=survey_id))

#
# # Analyse data sets
# @graphs.route("/analyse", methods=['GET', 'POST'])
# @login_required
# def analyse():
#     form = StatisticalTestForm()
#     # Get a list of all surveys associate with the current user
#     surveys = list(mongo.db.surveys.find({"user": current_user._id}))
#     for survey in surveys:
#         # Loop through each survey, saving the title (and filename) as well as the variables in the select options
#         form.survey.choices.append((survey["_id"], survey["title"]))
#         df = pd.read_csv(os.path.join(current_app.root_path, "uploads", survey["fileName"]))
#         for variable in list(df.columns.values):
#             form.independent_variable.choices.append((variable, variable))
#             form.dependent_variable.choices.append((variable, variable))
#     if form.validate_on_submit():
#         # Get the dataset, and save the variables in python variables
#         survey = mongo.db.surveys.find_one({"_id": form.survey.data})
#         df = pd.read_csv(os.path.join(current_app.root_path, "uploads", file_obj["fileName"]))
#         independent_variable = form.independent_variable.data
#         dependent_variable = form.dependent_variable.data
#         test = form.test.data
#         if test == "Kruskall Wallis Test":
#             kruskal_result = kruskal(data=df, dv=dependent_variable, between=independent_variable)
#             p_value = kruskal_result["p-unc"][0]
#         return redirect(url_for('graphs.result',\
#                                 survey=survey["_id"],\
#                                 test=test,\
#                                 p_value=p_value,\
#                                 independent_variable=independent_variable,\
#                                 dependent_variable=dependent_variable))
#     return render_template("analysedata.html", form=form)




# Analyse data sets
@graphs.route("/analyse", methods=['GET', 'POST'])
@login_required
def analyse():
    form = StatisticalTestForm()
    survey_id = request.args.get("survey_id")
    survey = mongo.db.surveys.find_one_or_404({"_id": ObjectId(survey_id)})
    if survey["user"] != current_user._id:
        flash("You do not have access to that page", "error")
        abort(403)
    df = pd.read_csv(os.path.join(current_app.root_path, "uploads", survey["fileName"]))
    for variable in list(df.columns.values):
        form.independent_variable.choices.append((variable, variable))
        form.dependent_variable.choices.append((variable, variable))
    if form.validate_on_submit():
        # Get the dataset, and save the variables in python variables
        independent_variable = form.independent_variable.data
        dependent_variable = form.dependent_variable.data
        test = form.test.data
        if test == "Kruskall Wallis Test":
            kruskal_result = kruskal(data=df, dv=dependent_variable, between=independent_variable)
            # get the p-value (p-unc) from the kruskal test and convert to 4 decimal places only
            p_value = "%.4f" % kruskal_result["p-unc"][0]
        return redirect(url_for('graphs.result',\
                                survey=survey_id,\
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
        {"$set":{"surveyId" : survey,\
                "user" : current_user._id,\
                "title" : form.title.data,\
                "test" : test,\
                "independentVariable" : independent_variable,\
                "dependentVariable" : dependent_variable,\
                "p" : p_value}}, upsert=True)
        return redirect(url_for('graphs.dashboard', title="Home", survey_id=survey))
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
    df = pd.read_csv(os.path.join(current_app.root_path, "uploads", file_obj["fileName"]))
    rows = len(df.index)
    cols = len(df.columns)
    column_info = parse_data(df);
    return render_template("quickstats.html", rows=rows, cols=cols, column_info=column_info, survey_id=survey_id )




# A 'helper' route that will return all the tests and graphs associated with a survey
# Used by a javscript 'fetch' function for creating dynamic homepage
@graphs.route("/home/<survey_id>")
def get_survey(survey_id):
    graphs = dumps(list(mongo.db.graphs.find({"surveyId": survey_id})))
    print(graphs)
    tests = list(mongo.db.tests.find({"surveyId": survey_id}))
    return jsonify({"graphs" : graphs, "tests" : tests})


# A 'helper' route that will return all the variables associated with a survey when called.
# Used by a javscript 'fetch' function for creating dynamic drop down boxes, with options changing based on previous options
@graphs.route("/analyse/<survey_id>")
def get_variables(survey_id):
    survey = mongo.db.surveys.find_one({"_id": ObjectId(survey_id)})
    df = pd.read_csv(os.path.join(current_app.root_path, "uploads", survey["fileName"]))
    column_info = parse_data(df)
    independent_variables = []
    dependent_variables = []
    for column in column_info:
        independent_variables.append(column["title"])
        if column["data_type"] == "numerical":
            dependent_variables.append(column["title"])
    return jsonify({"independentVariables" : independent_variables, "dependentVariables" : dependent_variables})
