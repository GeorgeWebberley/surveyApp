from surveyapp import mongo, login_manager
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

# methods inside this class allow for login_manager assistance
# when a user is logged in then it creates an instance of the session (called 'current_user')
# the static methods can then be called for various checks
# (e.g. "is_authenticated" allows me to check if a user is logged in or not and carry out appropriate redirects)
class User:
    def __init__(self, email, first_name, last_name, _id):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self._id = _id

    # My own version of the methods provided by UserMixin, adapted for use with MongoDB
    # https://flask-login.readthedocs.io/en/latest/#flask_login.UserMixin
    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.email

    # taken from the flask-login documentation https://flask-login.readthedocs.io/en/latest/
    # used to reload a user object from the user id stored in the session
    @login_manager.user_loader
    def load_user(email):
        user = mongo.db.users.find_one({"email" : email})
        if not user:
            return None
        return User(email=user["email"], first_name=user["firstName"], last_name=user["lastName"], _id=user["_id"])


    def get_reset_token(self, expires=1800):
        serializer = Serializer(current_app.config['SECRET_KEY'], expires)
        return serializer.dumps({'user_email': self.email}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        serializer = Serializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(token)['user_email']
        except:
            return None
        return mongo.db.users.find_one({"email" : email})
