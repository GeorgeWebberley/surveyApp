from surveyapp import mongo
from flask import render_template, request, Blueprint, url_for, redirect, flash


# Imports specifically for the feedback form
from surveyapp.main.forms import FeedbackForm
from flask_login import login_required, current_user


main = Blueprint("main", __name__)


@main.route('/')
@main.route('/index')
def index():
    return render_template("main/index.html")

# Feedback route to gather user feedback during development
@main.route('/feedback', methods=["GET", "POST"])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        mongo.db.feedback.insert_one({\
        "UI_2" : form.user_interface.data,\
        "functionality_2" : form.functionality.data,\
        "comments_2" : form.comments.data,\
        "user" : current_user._id})
        flash("Thank you for your feedback.", "success")
        return redirect(url_for("main.index"))
    return render_template("main/feedback.html", title = "Feedback", form = form)
