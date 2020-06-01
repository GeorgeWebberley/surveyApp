- [Full installation list](#installs)

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
pip3 install Flask
```

##### Flask-WTF

Flask-WTF is a wrapper around the WTForms package, including CSRF, file upload, and reCAPTCHA.

```
pip3 install flask-wtf
```

##### email_validator

It may also be necessary to install email_validator if not included in your version of Flask-WTF.

```
pip3 email_validator
```

##### Flask-Dropzone

For dragging and dropping of files onto the webpage for uploading.

```
pip install Flask-Dropzone
```
