from flask import Flask
from config import Config
from flask_dropzone import Dropzone

app = Flask(__name__)
app.config.from_object(Config)
dropzone = Dropzone(app)
# Only allow excel spreadsheets or csv files to be uploaded
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.xls, .xlt, .xla, .xlsx, .xltx, .xlsb, .xlsm, .xltm, .xlam, .csv'
app.config['DROPZONE_INVALID_FILE_TYPE'] = 'Only Excel files or CSV files can be used.'
# Set only one file upload at a time for the moment
app.config['DROPZONE_MAX_FILES'] = '1'

from app import routes
