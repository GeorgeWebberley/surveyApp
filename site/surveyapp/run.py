# Imports from the __init__.py file inside the surveyApp package
from surveyapp import create_app

# Creates instantiation of the app
app = create_app("dev")

if __name__ == '__main__':
    app.run(debug=True)
