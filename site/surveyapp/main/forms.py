from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired


# Form used to gather user feedback
class FeedbackForm(FlaskForm):
    user_interface = RadioField('How would you rate the user interface? (1 = bad, 10 = good)',
    validators=[DataRequired()], choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    functionality = RadioField('How well does the app do what you want it to? (1 = not well, 10 = well)',
    validators=[DataRequired()], choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    comments = TextAreaField('Any additional comments?')
    submit = SubmitField('Submit')
