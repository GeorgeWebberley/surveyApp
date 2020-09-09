import os

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'you-will-never-guess'
    # MongoDB configurations
    MONGO_URI = os.environ.get("MONGO_URI")
    # Email configurations
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEBUG = True
    MAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')




class TestingConfig(object):
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    MONGO_URI = "mongodb://localhost:27017/surveyDatabaseTest"
    SECRET_KEY = 'test!'
    # disabled so we can test login/registration
    WTF_CSRF_ENABLED = False
    # LOGIN_DISABLED = True

config_by_name = dict(
    dev=Config,
    test=TestingConfig
)

key = Config.SECRET_KEY
