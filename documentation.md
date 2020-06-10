To start running the application, first carry out all the installations on the [installation list](#installs).

The flask application then needs to know which file to be run when starting the app. These are currently set inside the ['.flaskenv'](./site/.flaskenv) file. It is therefore possible to run the application in develeoper mode (with debugging on) simply by running:

```
flask run
```

Simply edit the '.flasenv' file for running in a different environment.

<a name="installs"></a>

## Full installation list

### MacOS

Instructions assume [Homebrew](https://brew.sh/) is already installed on your OSX host.

### python 3

Used as the backend language for the project, handling server connections and database connections and for processing data used in the application.

```
brew install python
```

For installing python modules, it is advisable to create a virtual environment to help keep python modules specific to the project.

```
python3 -m virtualenv env
```

Activate the virtual environment before installing python modules.

```
source env/bin/activate
```

### MongoDB

The NoSQL database used for the application.

If not already tapped 'MongoDB Homebrew Tap':

```
brew tap mongodb/brew
```

Now it is possible to install MongoDB Community Edition.

```
brew install mongodb-community@4.2
```

### D3.js

D3.js is used to create the different data visualisations used in the app, such as bar charts and line graphs. To install using [NPM](https://www.npmjs.com/get-npm), first initialise an NPM.

```
npm init
```

Then install D3.js and all of its dependencies.

```
npm install --save d3
```

And then include the following line in the HTML.

```
<script type="text/javascript" src="node_modules/d3/build/d3.js"></script>
```

### Flask and its extensions

Flask is a microframework of python that provides many of the tools required for building a web application, such as templating, routing and Web Server Gateway Interface (WSGI).
As it is a 'microframework', it is often also required to install several extensions to get more functionality.
The dependencies that are included are:

- jinja2 - the templating engine.
- Werkzeug - a WSGI utility library.

For installing flask (from within the virtual environment).

```
pip install Flask
```

##### Flask-WTF

Flask-WTF is a wrapper around the WTForms package, including CSRF, file upload, and reCAPTCHA.

```
pip install flask-wtf
```

##### email_validator

It may also be necessary to install email_validator if not included in your version of Flask-WTF.

```
pip install email_validator
```

##### Flask-Dropzone

For dragging and dropping of files onto the webpage for uploading.

```
pip install Flask-Dropzone
```
##### Flask-PyMongo

For connecting and interacting with a MongoDB database

```
pip install Flask-PyMongo
```
##### python-dotenv

For managing data within .env files

```
pip install python-dotenv
```

##### Flask-Bcrypt

For hashing passwords to store in a database.

```
pip install flask-bcrypt
```

##### Flask-Login

Handles user session for flask applications, including loggin in, logging out and remember user sessions over time.

```
pip install flask-login
```

##### pytest

For carrying out unit testing of my code.

```
pip install pytest
```

##### pipenv

For easy installation of all packages.

```
pip install pipenv
```

##### pandas

For easy installation of all packages.

```
pip install pandas
```



## New Commands

Pre-requirements:
* Python 3.7.7
* Homebrew

To install all the packages you first need to install the latest version of [pipenv](https://pypi.org/project/pipenv/) onto your machine. To do this, run the following command (Note: it must be this latest version.)

```
pip install 'pipenv==2018.11.26'
```

Clone the git repository and navigate into the directory.
Then run the following command to install all the relevant packages.

```
pipenv install
```
