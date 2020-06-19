from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from surveyapp import mongo, login_manager



class RegistrationForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired(), Length(max=30)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(max=30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # This method follows the custom validator pattern outlined in WTForms documentation
    def validate_email(self, email):
        users = mongo.db.users
        user_exists = users.find_one({"email" : email.data})
        if user_exists:
            raise ValidationError("Account already exists with that email address.")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired(), Length(max=30)])
    last_name = StringField('Last name', validators=[DataRequired(), Length(max=30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')






class FeedbackForm(FlaskForm):
    user_interface = RadioField('How would you rate the user interface? (1 = bad, 10 = good)',
    validators=[DataRequired()], choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    functionality = RadioField('How well does the app do what you want it to? (1 = not well, 10 = well)',
    validators=[DataRequired()], choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    comments = TextAreaField('Any additional comments?')
    submit = SubmitField('Submit')
