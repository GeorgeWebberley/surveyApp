import threading

from flask import Flask, render_template, url_for, request, Blueprint, flash, redirect, abort, current_app
from flask_login import login_required, current_user
from surveyapp.surveys.forms import UploadForm, EditForm
from surveyapp import mongo
from bson.objectid import ObjectId

from surveyapp.graphs.utils import delete_image
from surveyapp.analysis.utils import run_all_tests
from surveyapp.surveys.utils import save_file, read_file, delete_file

surveys = Blueprint("surveys", __name__)

# Home page, displaying all the user's surveys as well as notifications
@surveys.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    surveys=mongo.db.surveys.find({"user":current_user._id})
    survey_list = []
    # Loop through each survey, counting the number of graphs and tests
    for survey in surveys:
        graphs = mongo.db.graphs.count_documents({"surveyId":survey["_id"]})
        tests = mongo.db.graphs.count_documents({"surveyId":survey["_id"]})
        # Send information to home page regarding the surveys, number of graphs and tests
        survey_list.append({"title": survey["title"],\
                            "_id": survey["_id"],\
                            "numGraphs": graphs,\
                            "numTests": tests})
    # Get the number of notifications (if any)
    notifications = mongo.db.temp_results.count_documents({"user": current_user._id})
    return render_template("surveys/home.html", title="Home", surveys=survey_list, notifications=notifications)



# Dasboard page for each survey
# Renders a page with all graphs and surveys relating to the chosen survey
@surveys.route('/home/<survey_id>', methods=['GET', 'POST'])
@login_required
def dashboard(survey_id):
    # Get the current survey
    survey = mongo.db.surveys.find_one_or_404({"_id": ObjectId(survey_id)})
    # Get the graphs and tests associated with that survey
    graphs = mongo.db.graphs.find({"surveyId":survey_id})
    tests = mongo.db.tests.find({"surveyId":survey_id})
    return render_template("surveys/dashboard.html", title="Dashboard", graphs=list(graphs), tests=list(tests), survey=survey)




@surveys.route('/import', methods=['GET', 'POST'])
# login required decorator prevents people accessing the page when not logged in
@login_required
def import_file():
    form = UploadForm()
    # Checks validation when form is submitted with submit button
    if form.validate_on_submit():
        file_name = save_file(form.file.data)
        survey_id = mongo.db.surveys.insert_one({
        "fileName" : file_name,
        "user" : current_user._id,
        "title" : form.title.data}).inserted_id  # Get the id of the survey just inserted
        flash("File uploaded successfully!", "success")
        # Running all the statistical tests on the data can take a lot of time. Therefore I
        # carry it out using a python thread. It is important to pass the current application,
        # so that the threaded function can be carried out from the current application context
        thread = threading.Thread(target=run_all_tests, args=(str(survey_id), current_user._id, current_app._get_current_object()), daemon=True)
        thread.start()
        return redirect(url_for("surveys.input", survey_id=survey_id))
    return render_template("surveys/import.html", title = "Import", form=form)


@surveys.route('/input', methods=['GET', 'POST'])
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
    return render_template("surveys/input.html", title="Input", data=data, survey_id=survey_id, form=form)





@surveys.route('/findings', methods=['GET', 'POST'])
@login_required
def findings():
    form = EditForm()
    notifications = mongo.db.temp_results.find({"user": current_user._id})
    if form.validate_on_submit():
        survey_id = request.args.get("survey_id")
        test = request.args.get("test")
        independent_variable = request.args.get("independent_variable")
        dependent_variable = request.args.get("dependent_variable")
        p_value = request.args.get("p")
        result_id = request.args.get("result_id")
        mongo.db.tests.insert_one({"surveyId" : survey_id,
                "user" : current_user._id,
                "title" : form.title.data,
                "test" : test,\
                "independentVariable" : independent_variable,\
                "dependentVariable" : dependent_variable,\
                "p" : p_value})
        mongo.db.temp_results.delete_one({'_id': ObjectId(result_id)})
        notifications = mongo.db.temp_results.find({"user": current_user._id})
        flash("Statistical test saved to your survey dashboard", "success")
        return redirect(url_for("surveys.findings"))
    return render_template("surveys/findings.html", title="Findings", form=form, notifications=notifications, count=notifications.count())


# Delete a temporary result
@surveys.route('/findings/<result_id>/delete', methods=['POST'])
@login_required
def delete_temp_result(result_id):
    file_obj = mongo.db.temp_results.find_one_or_404({"_id":ObjectId(result_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        abort(403)
    mongo.db.temp_results.delete_one(file_obj)
    return redirect(url_for('surveys.findings'))



# Delete all temporary results
@surveys.route('/findings/delete', methods=['POST'])
@login_required
def delete_findings():
    mongo.db.temp_results.delete_many({"user":current_user._id})
    return redirect(url_for('surveys.findings'))




# DELETE A SURVEY
@surveys.route("/survey/<survey_id>/delete", methods=['POST'])
@login_required
def delete_survey(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        abort(403)
    # First loop through all graphs, tests and remp results associated with that survey and delete them
    graphs = mongo.db.graphs.find({"surveyId":survey_id})
    for graph in graphs:
        delete_image(graph["image"])
        mongo.db.graphs.delete_one(graph)
    tests = mongo.db.tests.find({"surveyId":survey_id})
    for test in tests:
        mongo.db.tests.delete_one(test)
    temp_results = mongo.db.temp_results.find({"survey_id":survey_id})
    for result in temp_results:
        mongo.db.temp_results.delete_one(result)
    delete_file(file_obj["fileName"])
    mongo.db.surveys.delete_one(file_obj)
    return redirect(url_for('surveys.home'))
