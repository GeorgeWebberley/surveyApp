from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired

# Original form used to gather user feedback for sprints 1-3
class FeedbackForm(FlaskForm):
    user_interface = RadioField('How would you rate the user interface? (1 = bad, 10 = good)',
    validators=[DataRequired()], choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("10", "10")])
    functionality = RadioField('How well does the app do what you want it to? (1 = not well, 10 = well)',
    validators=[DataRequired()], choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("10", "10")])
    comments = TextAreaField('Any additional comments?')
    submit = SubmitField('Submit')

# Form used for final user feedback, with more questions
class FeedbackForm(FlaskForm):
    enough_graphs = RadioField('Do you feel there are enough graphs to visualise the different types of data you might have?',
    validators=[DataRequired()], choices=[("1", "Strongly disagree"), ("2", "Disagree"), ("3", "Neutral"), ("4", "Agree"), ("5", "Strongly agree")])
    good_graphs = RadioField('Do you feel that the graphs visualise the data as you expected?',
    validators=[DataRequired()], choices=[("1", "Strongly disagree"), ("2", "Disagree"), ("3", "Neutral"), ("4", "Agree"), ("5", "Strongly agree")])
    enough_tests = RadioField('Do you feel there are enough statistical tests to derive meaning from your data?',
    validators=[DataRequired()], choices=[("1", "Strongly disagree"), ("2", "Disagree"), ("3", "Neutral"), ("4", "Agree"), ("5", "Strongly agree")])
    auto_tests = RadioField('Was the auto-test feature helpful (automatic generation of statistical tests with significant results after form upload)?',
    validators=[DataRequired()], choices=[("1", "Strongly disagree"), ("2", "Disagree"), ("3", "Neutral"), ("4", "Agree"), ("5", "Strongly agree")])
    navigation = RadioField('How easy is it to navigate the website?',
    validators=[DataRequired()], choices=[("1", "Very difficult"), ("2", "Difficult"), ("3", "Neutral"), ("4", "Easy"), ("5", "Very easy")])
    data_input = RadioField('Was uploading or entering and editing data manually easy?',
    validators=[DataRequired()], choices=[("1", "Very difficult"), ("2", "Difficult"), ("3", "Neutral"), ("4", "Easy"), ("5", "Very easy")])
    # KEEP THIS ONE????
    export = RadioField('You were able to export your graphs easily.',
    validators=[DataRequired()], choices=[("1", "Strongly disagree"), ("2", "Disagree"), ("3", "Neutral"), ("4", "Agree"), ("5", "Stronlgy agree")])
    # ------
    effort = RadioField('How much effort did you have to personally put in to achieve what you wanted?',
    validators=[DataRequired()], choices=[ ("1", "Very much effort"), ("2", "Much effort"), ("3", "Medium effort"), ("4", "little effort"), ("5", "Very little effort")])
    future_use = RadioField('How likely would you be to use this application in the future?',
    validators=[DataRequired()], choices=[("1", "Very unlikely"), ("2", "Unlikely"), ("3", "Neutral"), ("4", "Likely"), ("5", "Very likely")])
    user_interface = RadioField('How would you rate the user interface as a whole? (1 = bad, 10 = good)',
    validators=[DataRequired()], choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("10", "10")])
    functionality = RadioField('How well does the app do what you want it to as a whole? (1 = not well, 10 = well)',
    validators=[DataRequired()], choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("10", "10")])
    comments = TextAreaField('Comments (if any)')
    submit = SubmitField('Submit')
