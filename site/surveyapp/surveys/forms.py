from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    title = StringField("Enter a title for this data.", validators=[DataRequired()])
    file = FileField("Choose file to upload", validators=[DataRequired(), FileAllowed(["xls", "xlt", "xla", "xlsx", "xltx", "xlsb", "xlsm", "xltm", "xlam", "csv"], message="Only CSV files or Excel Spreadsheets allowed.")])
    submit = SubmitField("Save and proceed")

# General form, used for editing a title. Used on survey input page and stat result page.
class EditForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    submit = SubmitField("Save")
