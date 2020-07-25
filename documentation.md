## Setup guide
To start running the application, first carry out the installations listed below.

### MacOS

Instructions assume [Homebrew](https://brew.sh/) is already installed on your OSX host.

### python 3

Used as the backend language for the project, handling server connections and database connections and for processing data used in the application.

```
brew install python
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

For saving graphs produced by D3, I use 'saveSvgAsPng' and 'canvg'

```
npm install save-svg-as-png
npm install canvg
```


### Python packages

For installing our python packages we will be using [pipenv](https://pypi.org/project/pipenv/) which will also handle our virtual environment for us. To do this, run the following command (Note: it must be this latest version.)

```
pip install 'pipenv==2018.11.26'
```

Clone the git repository and navigate into the directory.
Then run the following command to install all the relevant packages.

```
pipenv install
```

If you would like to also install the dev dependencies, including 'pytest' for testing, then instead run:

```
pipenv install --dev
```

With this method there is no need to create a virtual environment, it is handled for you automatically by pipenv.
Following the installations, you can then enter that virtual environment by using:

```
pipenv shell
```

Then to run the application, navigate to the 'site' directory and run 'flask run'

```
cd site
flask run
```

The flask application knows which file needs to be run when starting the app from the environment variables set in ['.flaskenv'](./site/.flaskenv). At the moment, the .flaskenv file specifies the app to run in developer mode. Simply edit the '.flasenv' file for running in a different environment.

### Full packages list

All the python packages used are listed below for your information (along with the pip command for installing if you would rather do it that way instead.)

#### Flask and its extensions

Flask is a microframework of python that provides many of the tools required for building a web application, such as templating, routing and Web Server Gateway Interface (WSGI).
As it is a 'microframework', it is often also required to install several extensions to get more functionality.
The dependencies that are included are:

- jinja2 - the templating engine.
- Werkzeug - a WSGI utility library.

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

Handles user session for flask applications, including logging in, logging out and remember user sessions over time.

```
pip install flask-login
```

##### pytest

For carrying out unit testing of my code.

```
pip install pytest
```


##### pandas and xlrd

For easy installation of all packages (xlrd allows for parsing Excel files).

```
pip install pandas
pip install xlrd
```

##### SciPy and Pingouin

Used for carrying out the statistical tests on the data.

```
pip install scipy
pip install pingouin
```

##### Flask-JSGlue

Allows for building flask-like URLs in javascript. Useful for Jquery POSTs (using flask synteax such as url_for).

```
pip install Flask-JSGlue
```

##### pyspellchecker

For testing possible typos in the data.

```
pip install pyspellchecker
```
