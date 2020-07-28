import pytest
import os
from flask import url_for
from surveyapp import create_app, mongo

from flask_login import current_user
from werkzeug.datastructures import FileStorage

# To convert image to base 64
import base64


# ------APPLICATION INITIALISATION------
@pytest.fixture
def client():
    app = create_app("test")
    with app.test_client() as client:
        with app.app_context():
            mongo.db.drop_collection("users")
            mongo.db.drop_collection("surveys")
            mongo.db.drop_collection("tests")
            yield client


    # client = app.test_client()
    # Clear the test database-collection so can start tests with empty database.
    # mongo.db.drop_collection("users")
    # mongo.db.drop_collection("surveys")
    # yield client

# -------INDEX PAGE-------

# test we can load the page ok
def test_index_response(client):
    rv = client.get('/index', content_type="html/text")
    assert(rv.status_code == 200)

def test_index_content(client):
    rv = client.get('/index', content_type="html/text")

    # test that both 'Login' and 'Register' appear on index page (when user not logged in)
    assert b'Login' in rv.data
    assert b'Register' in rv.data
    # test that Logout does not appear on index page (when user not logged in)
    assert b'Logout' not in rv.data


# ------REGISTERING ACCOUNT------
# setting follow_redirects=True allows the app to carry out redirections following registration
def register(client, first_name, last_name, email, password, password2):
    return client.post('/register', data=dict(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        password2=password2
    ), follow_redirects=True)

# test we can load the page ok
def test_register_response(client):
    rv = client.get('/index', content_type="html/text")
    assert(rv.status_code == 200)

# make sure logging in and logging out works
def test_register(client):

    rv = register(client, "firstName", "lastName", "email", "password", "password")
    assert b'Invalid email address' in rv.data

    rv = register(client, "firstName", "lastName", "test@email.com", "pass", "pass")
    assert b'Field must be at least 6 characters long.' in rv.data

    rv = register(client, "firstName", "lastName", "test@email.com", "password", "differentPassword")
    assert b'Field must be equal to password.' in rv.data

    rv = register(client, "test", "name", "test@email.com", "password", "password")
    assert b'Account created successfully! You can now login.' in rv.data




# ------LOGIN------
# setting follow_redirects=True allows the app to carry out redirects following the post request
def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)




# make sure logging in and logging out works
def test_login_logout(client):
    # Create an account to test the login page
    rv = register(client, "test", "name", "test@email.com", "password", "password")
    assert b'Account created successfully! You can now login.' in rv.data

    # test login with incorrect details
    rv = login(client, "incorrect@email.com", "password")
    assert b'Invalid username or password' in rv.data
    assert b'Logged in successfully.' not in rv.data

    rv = login(client, "test@email.com", "incorrectPassword")
    assert b'Invalid username or password' in rv.data
    assert b'Logged in successfully.' not in rv.data

    # test login/logout with correct details
    rv = login(client, "test@email.com", "password")
    assert b'Logged in successfully.' in rv.data

    rv = logout(client)
    assert b'Logged out successfully.' in rv.data




# Test the home page
def test_home(client):

    # First try accessing home when not logged in
    rv = client.get('/home', content_type="html/text")
    # Check that the user was redirected
    assert(rv.status_code == 302)

    # Create an account to test the login page
    register(client, "test", "name", "test@email.com", "password", "password")
    login(client, "test@email.com", "password")

    # Now try accessing home when logged in
    rv = client.get('/home', content_type="html/text")
    assert(rv.status_code == 200)
    assert b'Your surveys' in rv.data
    assert b'Welcome, test' in rv.data
    # assert that the user has no surveys yet
    assert b'No surveys yet! Click here to add your first survey.' in rv.data


# Custom function for uploading a test file
def upload_file(client, name):
    test_file = os.path.join("/Users/georgewebberley/Documents/George/Masters/project/webApp/site/testfiles/test.xlsx")

    file = FileStorage(
        stream=open(test_file, "rb"),
        filename="test.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),

    return client.post("/import", data=dict(
        file = file,
        title = name
        ),
        content_type="multipart/form-data",
        follow_redirects=True)


def test_upload_file(client):
    # Create an account to test the import page
    register(client, "test", "name", "test@email.com", "password", "password")
    login(client, "test@email.com", "password")

    # First check no surveys
    rv = client.get('/home', content_type="html/text")
    assert b'No surveys yet! Click here to add your first survey.' in rv.data

    # Now upload a file
    rv = upload_file(client, "Test file")
    # Check file uploaded ok
    assert b'File uploaded successfully!' in rv.data

    # Now check survey exists on home
    rv = client.get('/home', content_type="html/text")

    # Check the file exists on the home page
    assert b'Test file' in rv.data
    # Check it no longer says the following line
    assert b'No surveys yet! Click here to add your first survey.' not in rv.data


def test_quick_stats(client):
    # Register and login
    register(client, "test", "name", "test@email.com", "password", "password")
    login(client, "test@email.com", "password")
    # Upload a file
    rv = upload_file(client, "Test file")

    # For testing, we can get the id of the survey safely by searching for the title,
    # as we know there is only one survey with that name.
    survey = mongo.db.surveys.find_one({"title": "Test file"})
    rv = client.get(url_for("analysis.quick_stats", survey_id=survey['_id']))
    # Now run some checks to ensure the page loads correctly
    assert(rv.status_code == 200)
    assert b'Quick Stats: Test file' in rv.data
    assert b'Gender' in rv.data
    assert b'Age' in rv.data
    assert b'Quantities' in rv.data



# Function tests getting the page, posting data to create statistical test and deleting the test
def test_statistical_test(client):
    # Register and login
    register(client, "test", "name", "test@email.com", "password", "password")
    login(client, "test@email.com", "password")
    # Upload a file
    rv = upload_file(client, "Test file")

    # For testing, we can get the id of the survey safely by searching for the title,
    # as we know there is only one survey with that name.
    survey = mongo.db.surveys.find_one({"title": "Test file"})

    # First confirm that there are no tests associated with this survey
    rv = client.get(url_for("surveys.dashboard", survey_id=survey['_id']))
    assert(rv.status_code == 200)
    assert b'No tests yet!' in rv.data

    rv = client.get(url_for("analysis.analyse", survey_id=survey['_id']))
    # Now run some checks to ensure the page loads correctly
    assert(rv.status_code == 200)
    assert b'What test would you like to apply?' in rv.data
    assert b'select an option' in rv.data
    assert b'continue' in rv.data


    # Now we will post some data for a dummy statistical test
    test = "Kruskall Wallis Test"
    independent_variable = "Gender"
    dependent_variable = "Age"
    rv = client.post(url_for("analysis.analyse", survey_id=survey['_id']),
    data=dict(test = test, independent_variable = independent_variable, dependent_variable = dependent_variable),
    follow_redirects=True)

    assert(rv.status_code == 200)
    assert b'Test results' in rv.data
    assert b'P-Value' in rv.data
    assert b'Significance Value' in rv.data
    assert b'Accept the null hypothesis' in rv.data

    # Now we will test saving the statistical test with some dummy data
    rv = client.post(url_for("analysis.result", test = test,
        independent_variable = independent_variable,
        dependent_variable = dependent_variable,
        survey=survey['_id'],
        p_value="1"),
        data=dict(title = "Example test"),
        follow_redirects=True)

    # Check that the test is saved and that it now exists on the dashboard
    assert b'Statistical test saved.' in rv.data
    assert b'Example test' in rv.data
    assert b'No tests yet!' not in rv.data

    # Now finally, let's test deleting the test
    example_test = mongo.db.tests.find_one({"title": "Example test"})
    rv = client.post(url_for("analysis.delete_test",
        survey_id = survey['_id'],
        test_id = example_test['_id']),
        follow_redirects=True)

    # Check that there are no tests left associated with this survey
    assert b'Example test' not in rv.data
    assert b'No tests yet!' in rv.data






# Custom function for uploading a test file
def upload_image():
    test_file = os.path.join("/Users/georgewebberley/Documents/George/Masters/project/webApp/site/testfiles/test_image.png")

    #
    # file = FileStorage(
    #     stream=open(test_file, "rb"),
    #     filename="test_image.png",
    #     content_type="image/png",
    # )

    return base64.b64encode(open(test_file, "rb").read()).decode()





# Function tests getting the page, posting data to create statistical test and deleting the test
def test_graph(client):
    # Register and login
    register(client, "test", "name", "test@email.com", "password", "password")
    login(client, "test@email.com", "password")
    # Upload a file
    rv = upload_file(client, "Test file")

    survey = mongo.db.surveys.find_one({"title": "Test file"})
    # First confirm that there are no graphs associated with this survey
    rv = client.get(url_for("surveys.dashboard", survey_id=survey['_id']))
    assert(rv.status_code == 200)
    assert b'No graphs yet!' in rv.data

    rv = client.get(url_for("graphs.choose_graph", survey_id=survey['_id']))
    # Now run some checks to ensure the page loads correctly with all graph types
    assert(rv.status_code == 200)
    assert b'What type of graph would you like to make?' in rv.data
    assert b'Bar Chart' in rv.data
    assert b'Scatter Chart' in rv.data
    assert b'Pie Chart' in rv.data

    # Now we will go through chart types one at a time, testing they all work

    # ------BAR CHART------
    rv = client.get(url_for("graphs.graph", survey_id=survey['_id'], chart_type = "Bar chart"))
    assert b'Choose an x-axis variable to get started' in rv.data
    assert b'Save as' in rv.data
    assert b'Export as PNG' in rv.data
    assert b'Save to dashboard' in rv.data
    assert b'select an option' in rv.data
    assert b'Aggregation:' in rv.data

    # Upload a picture for the graph
    file = upload_image()
    # Save a graph with a random hex string for the graph_id
    # rv = client.post(url_for("graphs.graph", survey_id=survey['_id'], chart_type = "Bar chart", graph_id="9165e5ae08e98280241a7c9f"),
    # data=dict(title="Example bar chart",
    #     chart_type = "Bar chart",
    #     x_axis="Gender",
    #     y_axis="Amount",
    #     y_axis_agg="",
    #     image=file),
    # follow_redirects=True)

    print(rv.data)
    # assert b'Graph saved to dashboard.' in rv.data
