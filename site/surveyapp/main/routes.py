from surveyapp import mongo
from flask import render_template, request, Blueprint


# Imports specifically for the feedback form
from surveyapp.main.forms import FeedbackForm
from flask_login import login_required


main = Blueprint("main", __name__)


@main.route('/')
@main.route('/index')
def index():
    return render_template("index.html")




# Feedback route to gather user feedback during development
@main.route('/feedback', methods=["GET", "POST"])
@login_required
def feedback():
    form = FeedbackForm()
    return render_template("feedback.html", title = "Feedback", form = form)
