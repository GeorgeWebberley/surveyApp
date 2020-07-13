import pytest

from surveyapp import create_app, mongo

from flask_login import current_user
from werkzeug.datastructures import FileStorage


# ------APPLICATION INITIALISATION------
@pytest.fixture
def client():
    app = create_app("test")
    client = app.test_client()
    # Clear the test database-collection so can start tests with empty database.
    mongo.db.drop_collection("users")
    yield client

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


# Test upload file
def test_upload_file(client):
    test_file = "test.xlsx"

    file = FileStorage(
        stream=open(test_file, "rb"),
        filename="test.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ),

    rv = client.post("/login", data=dict(
        file = file,
        title = "Test file"
        ),
        content_type="multipart/form-data",
        follow_redirects=True)
