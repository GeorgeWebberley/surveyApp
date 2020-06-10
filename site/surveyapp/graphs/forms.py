from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class UploadForm(FlaskForm):
    title = StringField("Enter a title for this data.", validators=[DataRequired()])
    file = FileField('Choose file to upload', validators=[DataRequired(), FileAllowed(["xls", "xlt", "xla", "xlsx", "xltx", "xlsb", "xlsm", "xltm", "xlam", "csv"], message="Only CSV files or Excel Spreadsheets allowed.")])
    submit = SubmitField('Save and proceed')

class EditSurveyForm(FlaskForm):
    title = StringField("Enter a new title.", validators=[DataRequired()])
    submit = SubmitField("Save changes")

# FileAllowed([".xls", ".xlt", ".xla", ".xlsx", ".xltx", ".xlsb", ".xlsm", ".xltm", ".xlam", ".csv"], message="Only CSV files or Excel Spreadsheets allowed.")
