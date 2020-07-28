from flask_wtf import FlaskForm
# from flask_wtf.file import FileField, FileAllowed
from wtforms import Form, StringField, SubmitField, SelectField, BooleanField, IntegerField, FormField, FieldList
from wtforms.validators import DataRequired, NumberRange


# Form used for pie charts and bar charts
class BarPieForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    # We will append variables to x/y axis choices based on the data
    x_axis = SelectField("Choose a variable:", choices=[("", " -- select an option -- ")])
    # Bar chart will default to "Amount" on y axis. Will also append all numerical variable types from the data set.
    y_axis = SelectField("Choose a variable:", choices=[("Amount", "Amount")])
    y_axis_agg = SelectField("Aggregation:", choices=[("Average", "Average"), ("Highest", "Highest"), ("Lowest", "Lowest"), ("Sum", "Sum")])
    submit = SubmitField("Save to dashboard")

# Scatter charts form needs x-axis and y-axis variables, as well as possible ranges
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
    submit = SubmitField("Save to dashboard")


# Histograms only need x-axis variable. However they also need a range and also group size
class HistogramForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    # We will append variables to x/y axis choices based on the data
    x_axis = SelectField("Choose a variable:", choices=[("", " -- select an option -- ")])
    x_axis_from = IntegerField("From")
    x_axis_to = IntegerField("To")
    group_size = IntegerField("Number of groups")
    submit = SubmitField("Save to dashboard")


class MapForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    variable = SelectField("Choose a variable:", choices=[("", " -- select an option -- ")])
    scope = SelectField("Choose a scope:", choices=[("World", "World"), ("Europe", "Europe"), ("Africa", "Africa"), ("South America", "South America"), ("Asia", "Asia"), ("Australia/Oceania", "Australia/Oceania"), ("North America", "North America"), ("United States of America", "United States of America")])
    submit = SubmitField("Save to dashboard")




# FileAllowed([".xls", ".xlt", ".xla", ".xlsx", ".xltx", ".xlsb", ".xlsm", ".xltm", ".xlam", ".csv"], message="Only CSV files or Excel Spreadsheets allowed.")
