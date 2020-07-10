from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import Form, StringField, PasswordField, SubmitField, FileField, SelectField, BooleanField, IntegerField, FormField, FieldList
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from bson.objectid import ObjectId

from wtforms import Label


class UploadForm(FlaskForm):
    title = StringField("Enter a title for this data.", validators=[DataRequired()])
    file = FileField("Choose file to upload", validators=[DataRequired(), FileAllowed(["xls", "xlt", "xla", "xlsx", "xltx", "xlsb", "xlsm", "xltm", "xlam", "csv"], message="Only CSV files or Excel Spreadsheets allowed.")])
    submit = SubmitField("Save and proceed")

# This form is used for editing a statistical test title and for editing a survey title
class EditForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    submit = SubmitField("Save")

# Form used for pie charts and bar charts
class BarPieForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    # We will append variables to x/y axis choices based on the data
    x_axis = SelectField("Choose a variable:", choices=[("", " -- select an option -- ")])
    # Bar chart will default to "Amount" on y axis. Will also append all numerical variable types from the data set.
    y_axis = SelectField("Choose a variable:", choices=[("Amount", "Amount")])
    y_axis_agg = SelectField("Aggregation:", choices=[("Average", "Average"), ("Highest", "Highest"), ("Lowest", "Lowest"), ("Sum", "Sum")])
    submit = SubmitField("Save")

class ScatterchartForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    # We will append variables to x/y axis choices based on the data
    x_axis = SelectField("Choose a variable:", choices=[("", " -- select an option -- ")])
    x_axis_from = IntegerField("From")
    x_axis_to = IntegerField("To")
    # Bar chart will default to "Amount" on y axis. Will also append all numerical variable types from the data set.
    y_axis = SelectField("Choose a variable:", choices=[("", " -- select an option -- ")])
    y_axis_from = IntegerField("From")
    y_axis_to = IntegerField("To")
    line = BooleanField("Add connecting line: ")
    submit = SubmitField("Save")

class StatisticalTestForm(FlaskForm):
    # We will append choices to drop down depending on the data and what is selected by the upser
    # as survey takes an objectId as the value, we need to initialise it and also tell it to coerce ObjectIds
    test = SelectField(choices=[("", " -- select an option -- "), ("Kruskall Wallis Test", "Kruskall Wallis Test"), ("Mann-Whitney U Test", "Mann-Whitney U Test"), ("Chi-Square Test", "Chi-Square Test"), ("Chi-Square goodness of fit", "Chi-Square goodness of fit")], validators=[DataRequired()])
    independent_variable = SelectField(choices=[("", " -- select an option -- ")], validators=[DataRequired()])
    # Having a second variable is optional in some tests (that only require a single variable) therefore have not included DataRequired()
    dependent_variable = SelectField(choices=[("", " -- select an option -- ")])
    submit = SubmitField("Continue")


class ChiGoodnessEntryForm(Form):
    key = StringField()
    expected = IntegerField(validators=[NumberRange(min=0, max=100)])


class ChiGoodnessForm(FlaskForm):
    field = FieldList(FormField(ChiGoodnessEntryForm))
    submit = SubmitField("Continue")





# FileAllowed([".xls", ".xlt", ".xla", ".xlsx", ".xltx", ".xlsb", ".xlsm", ".xltm", ".xlam", ".csv"], message="Only CSV files or Excel Spreadsheets allowed.")
