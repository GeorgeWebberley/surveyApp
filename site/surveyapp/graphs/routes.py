import json
from surveyapp import mongo
from flask import Flask, render_template, url_for, request, Blueprint, flash, redirect, abort
from flask_login import login_required, current_user
from surveyapp.graphs.forms import BarPieForm, ScatterchartForm, HistogramForm, MapForm
from bson.objectid import ObjectId

from surveyapp.graphs.utils import save_image, delete_image
from surveyapp.surveys.utils import parse_data, read_file


graphs = Blueprint("graphs", __name__)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)




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
    return render_template("graphs/choosegraph.html", title="Select Graph", survey_id=survey_id)



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
    column_info = parse_data(df)
    # Convert the dataframe to a dict of records to be handled by D3.js on the client side.
    chart_data = df.to_dict(orient='records')
    # ----------SAME ROUTE USED FOR BAR AND PIE CHART----------
    if chart_type == "Bar chart" or chart_type == "Pie chart":
        return pie_bar_chart(survey_id, column_info, chart_data, graph_id, file_obj["title"], chart_type)
    # ----------SCATTER CHART----------
    elif chart_type == "Scatter chart":
        return scatter_chart(survey_id, column_info, chart_data, graph_id, file_obj["title"])
    # ----------SCATTER CHART----------
    elif chart_type == "Histogram":
        return histogram(survey_id, column_info, chart_data, graph_id, file_obj["title"])
    # ----------SCATTER CHART----------
    elif chart_type == "Map":
        return map_chart(survey_id, column_info, chart_data, graph_id, file_obj["title"])
    else:
        flash("something went wrong", "danger")
        abort(404)




# Function that renders the bar-chart page
def map_chart(survey_id, column_info, chart_data, graph_id, title):
    form = MapForm()
    # Populate the form options.
    for column in column_info:
        form.variable.choices.append((column["title"], column["title"]))
    # Now we have specified the 'select' options for the form, we can check 'form.validate_on_submit'
    if form.validate_on_submit():
        image_data = request.form["image"]
        file_name = save_image(image_data, graph_id)
        # setting upsert=true in the update will create the entry if it doesn't yet exist, else it updates
        mongo.db.graphs.update_one({"_id": ObjectId(graph_id)},\
        {"$set": {"title" : form.title.data,\
                "surveyId": survey_id,\
                "user" : current_user._id,\
                "type" : "Map",\
                "variable" : form.variable.data,\
                "scope" : form.scope.data,\
                "image": file_name}}, upsert=True)

    # If we are editing the graph instead of creating new, we want to prepopulate the fields
    graph_obj = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})

    if graph_obj:
        form.variable.data = graph_obj["variable"]
        form.scope.data = graph_obj["scope"]
        form.title.data = graph_obj["title"]
    else:
        form.title.data = "Map chart - " + title

    data = {"chart_data": chart_data, "title": title, "column_info" : column_info}
    return render_template("graphs/map.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id, chart_type="Map")



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

    # If we are editing the graph instead of creating new, we want to prepopulate the fields
    graph_obj = mongo.db.graphs.find_one({"_id":ObjectId(graph_id)})

    if graph_obj:
        form.x_axis.data = graph_obj["xAxis"]
        form.y_axis.data = graph_obj["yAxis"]
        form.y_axis_agg.data = graph_obj["yAggregation"]
        form.title.data = graph_obj["title"]
    else:
        form.title.data = "Graph - " + title

    data = {"chart_data": chart_data, "title": title, "column_info" : column_info}
    if chart_type == "Bar chart":
        return render_template("graphs/barchart.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id, chart_type="Bar chart")
    else:
        return render_template("graphs/piechart.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id, chart_type="Pie chart")




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
    data = {"chart_data": chart_data, "title": title, "column_info" : column_info}
    return render_template("graphs/scatterchart.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id, chart_type="Scatter chart")




def histogram(survey_id, column_info, chart_data, graph_id, title):
    form = HistogramForm()
    for column in column_info:
        # Scatter charts require both x and y axis to have some numerical value (i.e. ordinal/interval but not categorical)
        if column["data_type"] == "numerical":
            # We insert a tuple, The first is the 'value' of the select, the second is the text displayed
            form.x_axis.choices.append((column["title"], column["title"]))
    # Now we have specified the 'select' options for the form, we can prevalidate for 'form.validate_on_submit'
    print("before")
    if form.errors:
        print(form.errors.items())
    if form.validate_on_submit():
        print("after")
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
                "image": file_name}}, upsert=True)

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
    return render_template("graphs/histogram.html", data=data, form=form, survey_id=survey_id, graph_id=graph_id, chart_type="Histogram")


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
    return redirect(url_for('surveys.dashboard', survey_id=survey_id))


#
# # A 'helper' route that will return all the variables associated with a survey when called.
# # Used by a javscript 'fetch' function for creating dynamic drop down boxes, with options changing based on previous options
# @graphs.route("/analyse/<survey_id>")
# def get_variables(survey_id):
#     survey = mongo.db.surveys.find_one({"_id": ObjectId(survey_id)})
#     df = read_file(file_obj["fileName"])
#     column_info = parse_data(df)
#     independent_variables = []
#     dependent_variables = []
#     for column in column_info:
#         independent_variables.append(column["title"])
#         if column["data_type"] == "numerical":
#             dependent_variables.append(column["title"])
#     return jsonify({"independentVariables" : independent_variables, "dependentVariables" : dependent_variables})
