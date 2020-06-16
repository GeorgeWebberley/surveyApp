from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


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
    # We will append variables to x/y axis choices based on the data
    survey = SelectField(choices=[("", " -- select an option -- ")], validators=[DataRequired()])
    # Bar chart will default to "Amount" on y axis. Will also append all numerical variable types from the data set.
    test = SelectField(choices=[("", " -- select an option -- "), ("kruskall", "Kruskall Wallis Test"), ("paired t", "Paired T Test"), ("chi", "Chi-Squared Test")], validators=[DataRequired()])
    independent_variable = SelectField(choices=[("", " -- select an option -- ")], validators=[DataRequired()])
    dependent_variable = SelectField(choices=[("", " -- select an option -- ")], validators=[DataRequired()])
    submit = SubmitField("Continue")

# FileAllowed([".xls", ".xlt", ".xla", ".xlsx", ".xltx", ".xlsb", ".xlsm", ".xltm", ".xlam", ".csv"], message="Only CSV files or Excel Spreadsheets allowed.")
