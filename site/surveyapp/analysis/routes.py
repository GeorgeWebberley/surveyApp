import pandas as pd
from pandas.api.types import is_string_dtype
from scipy.stats import chi2_contingency, chisquare
from pingouin import kruskal, mwu
from surveyapp import mongo
from flask import Flask, render_template, url_for, request, Blueprint, flash, redirect, abort, send_file
from flask_login import login_required, current_user
from surveyapp.analysis.forms import StatisticalTestForm, ChiGoodnessEntryForm, ChiGoodnessForm
from surveyapp.surveys.forms import EditForm
from bson.objectid import ObjectId

import tempfile
from xlsxwriter import Workbook

from surveyapp.surveys.utils import parse_data, read_file


analysis = Blueprint("analysis", __name__)


# Analyse data sets
# In this function, after failing validation I have chosen to render the template fresh
# rather than redirecting the user back to this route. This is so that the form fields
# remain filled in and the user doesn't have to re-enter their choices.
@analysis.route("/analyse/<survey_id>", methods=['GET', 'POST'])
@login_required
def analyse(survey_id):
    form = StatisticalTestForm()
    survey = mongo.db.surveys.find_one_or_404({"_id": ObjectId(survey_id)})
    if survey["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        abort(403)
    df = read_file(survey["fileName"])
    # Populate the select options in the form with all the variables
    for variable in list(df.columns.values):
        form.independent_variable.choices.append((variable, variable))
        form.dependent_variable.choices.append((variable, variable))
    if form.validate_on_submit():
        # Get the dataset, and save the variables in python variables
        independent_variable = form.independent_variable.data
        dependent_variable = form.dependent_variable.data
        # Ensure the user hasn't selected the same variable for both
        if independent_variable == dependent_variable:
            flash("You can't select the same variable for both.", "danger")
            return render_template("analysis/analysedata.html", form=form)
        test = form.test.data
        # If the user selects Chi-Square goodness fit then they are redirected to a separate URL
        if test == "Chi-Square goodness of fit":
            return redirect(url_for('analysis.chi_goodness', variable=independent_variable, survey_id=survey_id))
        # The other tests all require a dependent variable
        if dependent_variable == "":
            flash("You must select a dependent variable for this test.", "danger")
            return render_template("analysis/analysedata.html", form=form)
        if test == "Kruskall Wallis Test":
            if is_string_dtype(df[dependent_variable]):
                flash("Dependent Variable '" + dependent_variable + "' is not numeric.", "danger")
                return render_template("analysis/analysedata.html", form=form)
            kruskal_result = kruskal(data=df, dv=dependent_variable, between=independent_variable)
            # get the p-value (p-unc) from the kruskal test and convert to 4 decimal places only
            p_value = "%.4f" % kruskal_result["p-unc"][0]
        # AT THE MOMENT, THIS TEST IS 2 TAILED. MAY WANT TO ADD OPTIONS FOR 1 TAILED TESTS
        elif test == "Mann-Whitney U Test":
            if is_string_dtype(df[dependent_variable]):
                flash("Dependent Variable '" + dependent_variable + "' is not numeric.", "danger")
                return render_template("analysis/analysedata.html", form=form)
            group_by = df.groupby(independent_variable)
            group_array = [group_by.get_group(x) for x in group_by.groups]
            if len(group_array) != 2:
                flash("Independent variable '" + independent_variable + "' has too many groups, only 2 allowed for Mann-Whitney U Test.", "danger")
                return render_template("analysis/analysedata.html", form=form)
            x = group_array[0][dependent_variable].values
            y = group_array[1][dependent_variable].values
            mwu_result = mwu(x, y)
            p_value = "%.4f" % mwu_result['p-val'].values[0]
        elif test == "Chi-Square Test":
            contingency_table = pd.crosstab(df[independent_variable], df[dependent_variable])
            _, p_value, _, _ = chi2_contingency(contingency_table, correction=False)

        return redirect(url_for('analysis.result',
                                survey=survey_id,
                                test=test,
                                p_value=p_value,
                                independent_variable=independent_variable,
                                dependent_variable=dependent_variable))
    return render_template("analysis/analysedata.html", form=form)


# Chi goodness of fit - extra form for expected values
@analysis.route("/chi/<survey_id>/<variable>", methods=['GET', 'POST'])
@login_required
def chi_goodness(survey_id, variable):
    # Get survey object and datafram
    survey = mongo.db.surveys.find_one_or_404({"_id": ObjectId(survey_id)})
    df = read_file(survey["fileName"])
    group_by = df.groupby(variable)
    keys = list(group_by.groups.keys())
    # Populate the form with unique groups in the given variable
    key_list = []
    # Get the total count, so that we can check the expected distribution matches
    total_count = len(df.index)
    # Populate the keys objects, initialising "expected" to 0
    for key in keys:
        key_list.append({"expected": 0, "key": key})
    form = ChiGoodnessForm(field=key_list)
    if form.validate_on_submit():
        # Initialise lists for actual and expected ditributions in the data
        actual_distribution = []
        expected_distribution = []
        for key in keys:
            # For each group, we get the count in the data and append it to our list
            key_count = df[df[variable] == key].shape[0]
            actual_distribution.append(key_count)
            for input in form.field.data:
                if key == input['key']:
                    # Now we populate the expected count from the form data
                    expected_distribution.append(input['expected'])
        if sum(expected_distribution) == 0:
            _, p_value = chisquare(actual_distribution)
        else:
            _, p_value = chisquare(actual_distribution, expected_distribution)
        return redirect(url_for('analysis.result',
            survey=survey_id,
            test="Chi-Square goodness of fit",
            p_value=p_value,
            independent_variable=variable,))
    return render_template("analysis/chisquare.html", form=form, keys=keys, total=total_count)




# Results from stats test
@analysis.route("/result", methods=['GET', 'POST'])
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
    # Chi goodness does not have a dependent_variable
    if not dependent_variable:
        dependent_variable = ""
    # Get the survey variable so the test result can be saved and reference the survey
    survey_id=request.args.get("survey")
    test_id=request.args.get("test_id")
    if form.validate_on_submit():
        # 'upsert' creates entry if it does not yet exist
        mongo.db.tests.update_one({"_id": ObjectId(test_id)},
        {"$set":{"surveyId" : survey_id,
                "user" : current_user._id,
                "title" : form.title.data,
                "test" : test,
                "independentVariable" : independent_variable,
                "dependentVariable" : dependent_variable,
                "p" : p_value}}, upsert=True)
        flash("Statistical test saved.", "success")
        return redirect(url_for('surveys.dashboard', title="Dashboard", survey_id=survey_id))
    title=request.args.get("title")
    if title:
        # i.e. if test already exists and user is clicking to view/edit it
        form.title.data = title
    else:
        # Set the default title. Users can change this
        form.title.data = independent_variable + "/" + dependent_variable + ": " + test
    result = {"test":test, "p":p_value, "alpha":alpha, "iv":independent_variable, "dv":dependent_variable}
    return render_template("analysis/result.html", result=result, form=form, survey_id=survey_id)



# DELETE A statistical test
@analysis.route("/analyse/<survey_id>/<test_id>/delete", methods=['POST'])
@login_required
def delete_test(survey_id, test_id):
    test_obj = mongo.db.tests.find_one_or_404({"_id":ObjectId(test_id)})
    if test_obj["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        abort(403)
    mongo.db.tests.delete_one(test_obj)
    flash("Test deleted", "success")
    return redirect(url_for('surveys.dashboard', survey_id=survey_id))


# Give the user a quick overview of stats on the survey data
@analysis.route("/quickstats/<survey_id>", methods=['GET'])
@login_required
def quick_stats(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that page", "danger")
        abort(403)
    df = read_file(file_obj["fileName"])
    rows = len(df.index)
    cols = len(df.columns)
    column_info = parse_data(df);
    return render_template("analysis/quickstats.html", rows=rows, cols=cols, column_info=column_info, survey_id=survey_id, survey_title=file_obj["title"] )

# Give the user a quick overview of stats on the survey data
@analysis.route("/export_tests/<survey_id>", methods=['GET'])
@login_required
def export_tests(survey_id):
    file_obj = mongo.db.surveys.find_one_or_404({"_id":ObjectId(survey_id)})
    if file_obj["user"] != current_user._id:
        flash("You do not have access to that survey", "danger")
        abort(403)
    tests = mongo.db.tests.find({"surveyId":survey_id})
    if tests.count() == 0:
        flash("You do not yet have any statistical tests for this survey!", "danger")
        return redirect(url_for('surveys.dashboard', survey_id=survey_id))    
    # Use a temp file so that it can be deleted after
    with tempfile.NamedTemporaryFile() as f:
        # Create a new excel workbook
        wb = Workbook(f.name)
        bold = wb.add_format({'bold': True})
        # grab the active worksheet
        ws = wb.add_worksheet()
        # Set the title and the column headers
        ws.write(0, 0, file_obj["title"], bold)
        # Create a table for the data. end of table will be the number of tests
        # +1 for the title and +1 for the column headers
        end_of_table = tests.count() + 2
        table_size = "A2:E" + str(end_of_table)
        ws.add_table(table_size, {
        'columns': [{'header': "Null Hypothesis"},
                  {'header': "Statistical Test"},
                  {'header': "Significance Value"},
                  {'header': "P-Value"},
                  {'header': "Conclusion"},
                  ]})
        # Row number is 2 since the first row is the header
        row_number = 2
        for test in tests:
            if float(test["p"]) < 0.05:
                conclusion = "Reject the null hypothesis."
            else:
                conclusion = "Accept the null hypothesis."
            ws.write(row_number, 0, get_null_hypothesis(test["test"], test["independentVariable"], test["dependentVariable"]))
            ws.write(row_number, 1, test["test"])
            ws.write(row_number, 2, 0.05)
            ws.write(row_number, 3, test["p"])
            ws.write(row_number, 4, conclusion)
            row_number += 1
        wb.close()
        return send_file(f.name, attachment_filename="tests.xlsx", as_attachment=True)

# gets the null hypothesis, depending on the type of test
def get_null_hypothesis(test, variable_1, variable_2):
    if test == "Chi-Square goodness of fit":
        return "There is no significant difference between the expected distribution of " + variable_1 + " and the observed distribution."
    elif test == "Chi-Square Test":
        return "There is no association between " + variable_1 + " and " + variable_2
    else:
        return "The distribution of " + variable_1 + " is the same across groups of " + variable_2
