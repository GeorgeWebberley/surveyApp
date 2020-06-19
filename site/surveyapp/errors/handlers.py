from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)

# Error handlers are initialised with '.app_errorhandler'. If you just want for this
# blueprint, can use 'errorhandler' instead. However I want for the full application.

# For a 404 error
@errors.app_errorhandler(404)
# Needs to be passed an error parameter
def error_404(error):
    return render_template('errors/404.html'), 404


# For a 403 error
@errors.app_errorhandler(403)
def error_404(error):
    return render_template('errors/403.html'), 403


# For a 500 error
@errors.app_errorhandler(500)
def error_404(error):
    return render_template('errors/500.html'), 500
