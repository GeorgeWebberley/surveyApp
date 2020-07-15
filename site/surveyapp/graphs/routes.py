import os
import secrets
import bson
import json
import pandas as pd
from pandas.api.types import is_string_dtype, is_numeric_dtype
# from pandas.api.types import is_numeric_dtype
import numpy as np
# from scipy.stats import kruskal
# from scipy.stats import mannwhitneyu
from scipy.stats import chi2_contingency, chisquare
import pingouin as pg
from pingouin import kruskal, mwu
from surveyapp import dropzone, mongo
from flask import Flask, render_template, url_for, request, Blueprint, flash, redirect, current_app, abort, jsonify
from flask_login import login_required, current_user
from surveyapp.graphs.forms import UploadForm, EditForm, BarPieForm, ScatterchartForm, HistogramForm, StatisticalTestForm, ChiGoodnessEntryForm, ChiGoodnessForm
from bson.objectid import ObjectId
from bson.json_util import loads, dumps
from surveyapp.graphs.utils import parse_data, save_graph, save_file, remove_nan, read_file, save_image, delete_image, delete_file


graphs = Blueprint("graphs", __name__)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)



@graphs.route('/import', methods=['GET', 'POST'])
# login required decorator prevents people accessing the page when not logged in
@login_required
def import_file():
    form = UploadForm()
    # Checks validation when form is submitted with submit button
    if form.validate_on_submit():
        file_name = save_file(form.file.data)
        survey_id = mongo.db.surveys.insert_one({\
        "fileName" : file_name,\
        "user" : current_user._id,\
        "title" : form.title.data}).inserted_id  # Get the id of the survey just inserted
        flash("File uploaded successfully!", "success")
        return redirect(url_for("graphs.input", survey_id=survey_id))
    return render_template("import.html", title = "Import", form=form)


@graphs.route('/input', methods=['GET', 'POST'])
@login_required
def input():
    # Initialise variables for handsontable (2d array for values, 1d array for column headers)
    value_list = [[]]
    header_list = []
    survey_id = request.args.get("survey_id")
    form = EditForm()
    # Handsontable data cannot be posted using normal WTForms methods.
    # Post needs to be from combined WTForm and AJAX
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
        survey = mongo.db.surveys.update_one({"_id": ObjectId(survey_id)},\
        {"$set": {"fileName" : file_name,\
                "user" : current_user._id,\
                "title" : form.title.data}}, upsert=True)
        survey_id = survey.upserted_id
        # Respond to the jquery POST with the survey_id. This is so that if the survey
        # was new, it can now be incorporated into subsequent POST requests to avoid multiple surveys being saved
        return str(survey_id)
    # If GET request and the survey already exists (i.e. editing an existing survey)
    elif request.method == "GET" and survey_id:
        file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
        if file_obj["user"] != current_user._id:
            flash("You do not have access to that page", "danger")
            return redirect(url_for("main.index"))
        # Read the file and extract the cell values and column headers
        df = read_file(file_obj["fileName"])
        value_list = df.values.tolist()
        header_list = df.columns.values.tolist()
        form.title.data = file_obj["title"]
    data = {"values": value_list, "headers": header_list}
    return render_template("input.html", title="Input", data=data, survey_id=survey_id, form=form)



@graphs.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    surveys=mongo.db.surveys.find({"user":current_user._id})
    survey_list = []
    for survey in surveys:
        graphs = mongo.db.graphs.count_documents({"surveyId":survey["_id"]})
        tests = mongo.db.graphs.count_documents({"surveyId":survey["_id"]})
        # Send information to home page regarding the surveys, number of graphs and tests
        survey_list.append({"title": survey["title"],\
                            "_id": survey["_id"],\
                            "numGraphs": graphs,\
                            "numTests": tests})
    return render_template("home.html", title="Home", surveys=survey_list)


# Dasboard page for each survey
# Renders a page with all graphs and surveys relating to the chosen survey
@graphs.route('/home/<survey_id>', methods=['GET', 'POST'])
@login_required
def dashboard(survey_id):
    survey = mongo.db.surveys.find_one_or_404({"_id": ObjectId(survey_id)})
    graphs = mongo.db.graphs.find({"surveyId":survey_id})
    tests = mongo.db.tests.find({"surveyId":survey_id})
    return render_template("dashboard.html", title="Dashboard", graphs=list(graphs), tests=list(tests), survey=survey)



# RELOOK AT THIS. AT THE MOMENT I AM SENDING THE FILE ID BACK AND FORTH FROM THE SERVER. MIGHT BE BETTER TO USE LOCAL STORAGE??
# IS PAGE NEEDED AT ALL? INSTEAD COULD HAVE A MODAL WHERE SUER SELECTS THE TYPE OF GRAPH THEY WANT
# Page where user chooses the type of graph they would like to create for their survey
@graphs.route('/choosegraph/<survey_id>', methods=['GET', 'POST'])
@login_required
def choose_graph(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        return redirect(url_for("main.index"))
    return render_template("choosegraph.html", title="Select Graph", survey_id=survey_id)



@graphs.route('/graph/<survey_id>', methods=['GET', 'POST'])
@login_required
def graph(survey_id):
    # Get the file object so that we can load the data
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        return redirect(url_for("main.index"))
    # Get the id of the graph (if it exists yet)
    graph_id = request.args.get("graph_id")
    graph_obj = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})
    # i.e. if user is choosing to edit an existing graph
    if graph_obj:
        chart_type = graph_obj["type"]
    # Else user is creating a new graph of a chosen type
    else:
        chart_type = request.args.get("chart_type")
    # Read the csv file in
    df = read_file(file_obj["fileName"])
    # parse the columns to get information regarding type of data
    # print(df)
    column_info, new_df = parse_data(df)
    # print(df)
    # Convert the dataframe to a dict of records to be handled by D3.js on the client side.
    chart_data = df.to_dict(orient='records')
    # print("chart_data")
    # print(chart_data)
    # ----------SAME ROUTE USED FOR BAR AND PIE CHART----------
    if chart_type == "Bar chart" or chart_type == "Pie chart":
        return pie_bar_chart(survey_id, column_info, chart_data, graph_id, file_obj["title"], chart_type)
    # ----------SCATTER CHART----------
    elif chart_type == "Scatter chart":
        return scatter_chart(survey_id, column_info, chart_data, graph_id, file_obj["title"])
    # ----------SCATTER CHART----------
    elif chart_type == "Histogram":
        return histogram(survey_id, column_info, chart_data, graph_id, file_obj["title"])
    else:
        flash("something went wrong", "danger")
        abort(404)


# Function that renders the bar-chart page
def pie_bar_chart(survey_id, column_info, chart_data, graph_id, title, chart_type):
    form = BarPieForm()
    # Populate the form options. A bar/pie chart can take any data type for x-axis but y-axis must be numerical
    for column in column_info:
        form.x_axis.choices.append((column["title"], column["title"]))
        if column["data_type"] == "numerical":
            # We insert a tuple, The first is the 'value' of the select, the second is the text displayed
            form.y_axis.choices.append((column["title"], column["title"]))
    # Now we have specified the 'select' options for the form, we can check 'form.validate_on_submit'
    if form.validate_on_submit():
        image_data = request.form["image"]
        file_name = save_image(image_data, graph_id)
        if form.y_axis.data == "Amount":
            y_agg = ""
        else:
            y_agg = form.y_axis_agg.data
        # setting upsert=true in the update will create the entry if it doesn't yet exist, else it updates
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)},\
        {"$set": {"title" : form.title.data,\
                "surveyId": survey_id,\
                "user" : current_user._id,\
                "type" : chart_type,\
                "xAxis" : form.x_axis.data,\
                "yAxis": form.y_axis.data,\
                "yAggregation": y_agg,
                "image": file_name}}, upsert=True)
        flash("Graph saved to dashboard.", "success")
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
    if chart_type == "Bar chart":
        return render_template("barchart.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id)
    else:
        return render_template("piechart.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id)




def scatter_chart(survey_id, column_info, chart_data, graph_id, title):
    form = ScatterchartForm()
    for column in column_info:
        # Scatter charts require both x and y axis to have some numerical value (i.e. ordinal/interval but not categorical)
        if column["data_type"] == "numerical":
            # We insert a tuple, The first is the 'value' of the select, the second is the text displayed
            form.x_axis.choices.append((column["title"], column["title"]))
            form.y_axis.choices.append((column["title"], column["title"]))
        if column["data_type"] == "date/time":
            # We insert a tuple, The first is the 'value' of the select, the second is the text displayed
            form.x_axis.choices.append((column["title"], column["title"]))
    # Now we have specified the 'select' options for the form, we can prevalidate for 'form.validate_on_submit'
    if form.validate_on_submit():
        image_data = request.form["image"]
        file_name = save_image(image_data, graph_id)
        # setting upsert=true in the update will create the entry if it doesn't yet exist, else it updates
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)},\
        {"$set": {"title" : form.title.data,\
                "surveyId": survey_id,\
                "user" : current_user._id,\
                "type" : "Scatter chart",\
                "xAxis" : form.x_axis.data,\
                "xAxisFrom" : form.x_axis_from.data,\
                "xAxisTo" : form.x_axis_to.data,\
                "yAxis": form.y_axis.data,\
                "yAxisFrom": form.y_axis_from.data,\
                "yAxisTo": form.y_axis_to.data,\
                "line": form.line.data,\
                "image": file_name}}, upsert=True)
        flash("Graph saved to dashboard.", "success")
        return redirect(url_for("graphs.dashboard", title="Dashboard", survey_id=survey_id))

    # If we are editing the graph instead of creating new, we want to prepopulate the fields
    graph_obj = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})

    if graph_obj:
        form.x_axis.data = graph_obj["xAxis"]
        form.x_axis_from.data = graph_obj["xAxisFrom"]
        form.x_axis_to.data = graph_obj["xAxisTo"]
        form.y_axis.data = graph_obj["yAxis"]
        form.y_axis_from.data = graph_obj["yAxisFrom"]
        form.y_axis_to.data = graph_obj["yAxisTo"]
        form.line.data = graph_obj["line"]
        form.title.data = graph_obj["title"]
    else:
        form.title.data = "Graph - " + title

    print("chart_data")
    print(chart_data)
    data = {"chart_data": chart_data, "title": title, "column_info" : column_info}
    return render_template("scatterchart.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id)




def histogram(survey_id, column_info, chart_data, graph_id, title):
    form = HistogramForm()
    for column in column_info:
        # Scatter charts require both x and y axis to have some numerical value (i.e. ordinal/interval but not categorical)
        if column["data_type"] == "numerical":
            # We insert a tuple, The first is the 'value' of the select, the second is the text displayed
            form.x_axis.choices.append((column["title"], column["title"]))
    # Now we have specified the 'select' options for the form, we can prevalidate for 'form.validate_on_submit'
    if form.validate_on_submit():
        image_data = request.form["image"]
        file_name = save_image(image_data, graph_id)
        # setting upsert=true in the update will create the entry if it doesn't yet exist, else it updates
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)},\
        {"$set": {"title" : form.title.data,\
                "surveyId": survey_id,\
                "user" : current_user._id,\
                "type" : "Histogram",\
                "xAxis" : form.x_axis.data,\
                "xAxisFrom" : form.x_axis_from.data,\
                "xAxisTo" : form.x_axis_to.data,\
                "groupSize" : form.group_size.data,\
                # "line": form.line.data,\
                "image": file_name}}, upsert=True)
        flash("Graph saved to dashboard.", "success")
        return redirect(url_for("graphs.dashboard", title="Dashboard", survey_id=survey_id))

    # If we are editing the graph instead of creating new, we want to prepopulate the fields
    graph_obj = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})

    if graph_obj:
        form.x_axis.data = graph_obj["xAxis"]
        form.x_axis_from.data = graph_obj["xAxisFrom"]
        form.x_axis_to.data = graph_obj["xAxisTo"]
        # form.line.data = graph_obj["line"]
        form.title.data = graph_obj["title"]
    else:
        form.title.data = "Graph - " + title

    data = {"chart_data": chart_data, "title": title, "column_info" : column_info}
    return render_template("histogram.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id)



# DELETE A SURVEY
@graphs.route("/survey/<survey_id>/delete", methods=['POST'])
@login_required
def delete_survey(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        abort(403)
    graphs = mongo.db.graphs.find({"surveyId":survey_id})
    for graph in graphs:
        delete_image(graph["image"])
        mongo.db.graphs.delete_one(graph)
    delete_file(file_obj["fileName"])
    mongo.db.surveys.delete_one(file_obj)
    return redirect(url_for('graphs.home'))


# EDIT A SURVEY
@graphs.route("/survey/<survey_id>/edit", methods=["GET", "POST"])
@login_required
def edit_survey(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
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
        flash("You do not have access to that page", "danger")
        abort(403)
    delete_image(graph_obj["image"])
    mongo.db.graphs.delete_one(graph_obj)
    return redirect(url_for('graphs.dashboard', survey_id=survey_id))


# Analyse data sets
@graphs.route("/analyse", methods=['GET', 'POST'])
@login_required
def analyse():
    form = StatisticalTestForm()
    survey_id = request.args.get("survey_id")
    survey = mongo.db.surveys.find_one_or_404({"_id": ObjectId(survey_id)})
    if survey["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        abort(403)
    df = read_file(survey["fileName"])
    for variable in list(df.columns.values):
        form.independent_variable.choices.append((variable, variable))
        form.dependent_variable.choices.append((variable, variable))
    if form.validate_on_submit():
        # Get the dataset, and save the variables in python variables
        independent_variable = form.independent_variable.data
        dependent_variable = form.dependent_variable.data
        if independent_variable == dependent_variable:
            flash("You can select the same variable for both.", "danger")
            return render_template("analysedata.html", form=form)
        test = form.test.data
        if test == "Kruskall Wallis Test":
            if dependent_variable == "":
                flash("You must select a dependent variable for this test.", "danger")
                return render_template("analysedata.html", form=form)
            if is_string_dtype(df[dependent_variable]):
                flash("Dependent Variable '" + dependent_variable + "' is not numeric.", "danger")
                return render_template("analysedata.html", form=form)
            kruskal_result = kruskal(data=df, dv=dependent_variable, between=independent_variable)
            # get the p-value (p-unc) from the kruskal test and convert to 4 decimal places only
            p_value = "%.4f" % kruskal_result["p-unc"][0]
        # AT THE MOMENT, THIS TEST IS 2 TAILED. MAY WANT TO ADD OPTIONS FOR 1 TAILED TESTS
        elif test == "Mann-Whitney U Test":
            if dependent_variable == "":
                flash("You must select a dependent variable for this test.", "danger")
                return render_template("analysedata.html", form=form)
            if is_string_dtype(df[dependent_variable]):
                flash("Dependent Variable '" + dependent_variable + "' is not numeric.", "danger")
                return render_template("analysedata.html", form=form)
            group_by = df.groupby(independent_variable)
            group_array = [group_by.get_group(x) for x in group_by.groups]
            if len(group_array) != 2:
                flash("Independent variable '" + independent_variable + "' has too many groups, only 2 allowed for Mann-Whitney U Test.", "danger")
                return render_template("analysedata.html", form=form)
            x = group_array[0][dependent_variable].values
            y = group_array[1][dependent_variable].values
            mwu_result = mwu(x, y)
            p_value = "%.4f" % mwu_result['p-val'].values[0]
        elif test == "Chi-Square Test":
            if dependent_variable == "":
                flash("You must select a dependent variable for this test.", "danger")
                return render_template("analysedata.html", form=form)
            contingency_table = pd.crosstab(df[independent_variable], df[dependent_variable])
            _, p_value, _, _ = chi2_contingency(contingency_table, correction=False)
        elif test == "Chi-Square goodness of fit":
            return redirect(url_for('graphs.chi_goodness', survey=survey_id, variable=independent_variable, survey_id=survey_id))
        return redirect(url_for('graphs.result',\
                                survey=survey_id,\
                                test=test,\
                                p_value=p_value,\
                                independent_variable=independent_variable,\
                                dependent_variable=dependent_variable))
    return render_template("analysedata.html", form=form)

# # Analyse data sets
# @graphs.route("/chi", methods=['GET', 'POST'])
# @login_required
# def chi_goodness():
#     # Get request arguments
#     survey_id = request.args.get("survey_id")
#     variable = request.args.get("variable")
#     # Get survey object and datafram
#     survey = mongo.db.surveys.find_one_or_404({"_id": ObjectId(survey_id)})
#     df = pd.read_csv(os.path.join(current_app.root_path, "uploads", survey["fileName"]))
#     group_by = df.groupby(variable)
#     # Populate the form with unique groups in the given variable
#     form = ChiGoodnessForm()
#     for key in group_by.groups.keys():
#         field_form = ChiGoodnessEntryForm()
#         field_form.expected.label.text = Label(field_id = "name", text = "Your New Field Description Goes Here.")
#         form.field.append_entry(field_form)
#     if form.validate_on_submit():
#         print("lol")
#     return render_template("chisquare.html", form=form, keys=list(group_by.groups.keys()))
#



# Chi goodness of fit - extra form for expected values
@graphs.route("/chi", methods=['GET', 'POST'])
@login_required
def chi_goodness():
    # Get request arguments
    survey_id = request.args.get("survey_id")
    variable = request.args.get("variable")
    # Get survey object and datafram
    survey = mongo.db.surveys.find_one_or_404({"_id": ObjectId(survey_id)})
    df = read_file(file_obj["fileName"])
    group_by = df.groupby(variable)
    keys = list(group_by.groups.keys())
    # Populate the form with unique groups in the given variable
    key_list = []
    for key in keys:
        key_list.append({"expected": 0, "key": key})
    form = ChiGoodnessForm(field=key_list)
    if form.validate_on_submit():
        total_count = len(df.index)
        actual_distribution = []
        expected_distribution = []
        for key in keys:
            key_count = df[df[variable] == key].shape[0]
            actual_distribution.append((key_count*100)/total_count)
            for input in form.field.data:
                if key == input['key']:
                    expected_distribution.append(input['expected'])
        if sum(expected_distribution) == 0:
            _, p_value = chisquare(actual_distribution)
        else:
            _, p_value = chisquare(actual_distribution, expected_distribution)
        return redirect(url_for('graphs.result',\
            survey=survey_id,\
            test="Chi-Square goodness of fit",\
            p_value=p_value,\
            independent_variable=variable,))

    return render_template("chisquare.html", form=form, keys=keys)




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
    if not dependent_variable:
        dependent_variable = ""
    # Get the survey variable so the test result can be saved and reference the survey
    survey_id=request.args.get("survey")
    test_id=request.args.get("test_id")
    if form.validate_on_submit():
        # 'upsert' creates entry if it does not yet exist
        mongo.db.tests.update_one({"_id": ObjectId(test_id)},\
        {"$set":{"surveyId" : survey_id,\
                "user" : current_user._id,\
                "title" : form.title.data,\
                "test" : test,\
                "independentVariable" : independent_variable,\
                "dependentVariable" : dependent_variable,\
                "p" : p_value}}, upsert=True)
        flash("Statistical test saved.", "success")
        return redirect(url_for('graphs.dashboard', title="Dashboard", survey_id=survey_id))
    title=request.args.get("title")
    if title:
        # i.e. if test already exists and user is clicking to view/edit it
        form.title.data = title
    else:
        # Set the default title. Users can change this
        form.title.data = independent_variable + "/" + dependent_variable + ": " + test
    result = {"test":test, "p":p_value, "alpha":alpha, "iv":independent_variable, "dv":dependent_variable}
    return render_template("result.html", result=result, form=form, survey_id=survey_id)



# DELETE A statistical test
@graphs.route("/analyse/<survey_id>/<test_id>/delete", methods=['POST'])
@login_required
def delete_test(survey_id, test_id):
    test_obj = mongo.db.tests.find_one_or_404({"_id":ObjectId(test_id)})
    if test_obj["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        abort(403)
    mongo.db.tests.delete_one(test_obj)
    flash("Test deleted", "success")
    return redirect(url_for('graphs.dashboard', survey_id=survey_id))




# Give the user a quick overview of stats on the survey data
@graphs.route("/quickstats/<survey_id>", methods=['GET'])
@login_required
def quick_stats(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        return redirect(url_for("main.index"))
    df = read_file(file_obj["fileName"])
    rows = len(df.index)
    cols = len(df.columns)
    column_info, _ = parse_data(df);
    return render_template("quickstats.html", rows=rows, cols=cols, column_info=column_info, survey_id=survey_id, survey_title=file_obj["title"] )




# A 'helper' route that will return all the tests and graphs associated with a survey
# Used by a javscript 'fetch' function for creating dynamic homepage
@graphs.route("/home/<survey_id>")
def get_survey(survey_id):
    graphs = dumps(list(mongo.db.graphs.find({"surveyId": survey_id})))
    tests = list(mongo.db.tests.find({"surveyId": survey_id}))
    return jsonify({"graphs" : graphs, "tests" : tests})


# A 'helper' route that will return all the variables associated with a survey when called.
# Used by a javscript 'fetch' function for creating dynamic drop down boxes, with options changing based on previous options
@graphs.route("/analyse/<survey_id>")
def get_variables(survey_id):
    survey = mongo.db.surveys.find_one({"_id": ObjectId(survey_id)})
    df = read_file(file_obj["fileName"])
    column_info, _ = parse_data(df)
    independent_variables = []
    dependent_variables = []
    for column in column_info:
        independent_variables.append(column["title"])
        if column["data_type"] == "numerical":
            dependent_variables.append(column["title"])
    return jsonify({"independentVariables" : independent_variables, "dependentVariables" : dependent_variables})
