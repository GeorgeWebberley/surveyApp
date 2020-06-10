from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
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
