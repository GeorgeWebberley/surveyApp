from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from bson.objectid import ObjectId


class UploadForm(FlaskForm):
    title = StringField("Enter a title for this data.", validators=[DataRequired()])
    file = FileField('Choose file to upload', validators=[DataRequired(), FileAllowed(["xls", "xlt", "xla", "xlsx", "xltx", "xlsb", "xlsm", "xltm", "xlam", "csv"], message="Only CSV files or Excel Spreadsheets allowed.")])
    submit = SubmitField('Save and proceed')

class EditSurveyForm(FlaskForm):
    title = StringField("Enter a new title.", validators=[DataRequired()])
    submit = SubmitField("Save changes")

class SaveGraphForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    # We will append variables to x/y axis choices based on the data
    x_axis = SelectField("Choose a variable:", choices=[("", " -- select an option -- ")])
    # Bar chart will default to "Amount" on y axis. Will also append all numerical variable types from the data set.
    y_axis = SelectField("Choose a variable:", choices=[("Amount", "Amount")])
    y_axis_agg = SelectField("Aggregation:", choices=[("Average", "Average"), ("Highest", "Highest"), ("Lowest", "Lowest"), ("Sum", "Sum")])
    submit = SubmitField("Save")

class StatisticalTestForm(FlaskForm):
    # We will append choices to drop down depending on the data and what is selected by the upser
    # as survey takes an objectId as the value, we need to initialise it and also tell it to coerce ObjectIds
    survey = SelectField(choices=[("000000000000000000000000", " -- select an option -- ")], coerce=ObjectId, validators=[DataRequired()])
    test = SelectField(choices=[("", " -- select an option -- "), ("Kruskall Wallis Test", "Kruskall Wallis Test"), ("Paired T Test", "Paired T Test"), ("Chi-Squared Test", "Chi-Squared Test")], validators=[DataRequired()])
    independent_variable = SelectField(choices=[("", " -- select an option -- ")], validators=[DataRequired()])
    dependent_variable = SelectField(choices=[("", " -- select an option -- ")], validators=[DataRequired()])
    submit = SubmitField("Continue")

# FileAllowed([".xls", ".xlt", ".xla", ".xlsx", ".xltx", ".xlsb", ".xlsm", ".xltm", ".xlam", ".csv"], message="Only CSV files or Excel Spreadsheets allowed.")
