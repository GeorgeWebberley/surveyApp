from flask_wtf import FlaskForm
from flask_login import current_user
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
    # When the form is validated, it checks if a user already exists with that email

    def validate_email(self, email):
        user_exists = mongo.db.users.find_one({"email" : email.data})
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
    submit = SubmitField('Update')

    # This method follows the custom validator pattern outlined in WTForms documentation
    # When the form is validated, it checks if a user already exists with that email
    def validate_email(self, email):
        if email.data != current_user.email:
            user_exists = mongo.db.users.find_one({"email" : email.data})
            if user_exists:
                raise ValidationError("Account already exists with that email address.")
