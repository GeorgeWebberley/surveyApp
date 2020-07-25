from flask import Flask
from surveyapp.config import config_by_name
# from surveyapp.config import Config
from flask_bcrypt import Bcrypt
from flask_dropzone import Dropzone
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_mail import Mail
from flask_jsglue import JSGlue


# extensions created outside the create_app function (but initialised inside the function)
dropzone = Dropzone()
# for database handling
mongo = PyMongo()
# for hashing passwords
bcrypt = Bcrypt()
# login_manager provides tools such as checking if user is logged in, logging in and out of session etc.
login_manager = LoginManager()
# redirects users who are not logged in back to the users.login page
login_manager.login_view = "users.login"
# adds a CSS class to the message that is displayed when attempting to access pages when not logged in
login_manager.login_message_category = "error"

mail = Mail()

jsglue = JSGlue()

# moving the app creation into a function allows for multiple instances of the app to made
# furthermore it allows for testing (as different testing instances can be made)
# this is following the flask factory pattern
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # initialise extensions
    dropzone.init_app(app)
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    jsglue.init_app(app)


    # Import the blueprints and register them with out app (so it knows where to look for the routes)
    from surveyapp.users.routes import users
    from surveyapp.graphs.routes import graphs
    from surveyapp.main.routes import main
    from surveyapp.errors.handlers import errors
    # Register the blueprint routes
    app.register_blueprint(users)
    app.register_blueprint(graphs)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
