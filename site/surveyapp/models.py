from surveyapp import mongo, login_manager

# methods inside this class allow for login_manager assistance
# when a user is logged in then it creates an instance of the session
# the static methods can then be called for various checks
# (e.g. "is_authenticated" allows me to check if a user is logged in or not and carry out appropriate redirects)
class User:
    def __init__(self, email):
        self.email = email

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
        users = mongo.db.users.find_one({"email" : email})
        if not users:
            return None
        return User(email=users["email"])
