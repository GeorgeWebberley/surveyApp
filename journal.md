# Project Journal

This is a development journal that will be kept for the project duration and updated regularly with my progress.
It will contain information regarding what has been achieved recently and what will be looked at next.
Any specific problems I encounter or reflections that I may have will also be included.

- [Jump to the latest entry](#latestEntry)

## Week 1

### Pre-project setup

###### Goals

- Setup the preliminary folder structure, kanban board and project journal. &#x2705;
- Initialise a local project Git repository and remote repository on Github. &#x2705;
- Ensure all initial tools and programming languages required to get the project started are ready and installed, including:
  * [python3](https://www.python.org/downloads/) (and setting up a virtual environment). &#x2705;

  * [Flask](https://flask.palletsprojects.com/en/1.1.x/installation/#installation). &#x2705;

  * Javascript (specifically [D3.js](https://d3js.org/)). &#x2705;

  * [MongoDB](https://www.mongodb.com/). &#x2705;

The full installation list will be kept up to date in the accompanying [code documentation](documentation.md#installs).

#### Preliminary System Design
The aim is to create an initial system design that will help in the initial stages of developing the web application. The design will be continuously reviewed and assessed following the start of implementation (influenced by problems encountered, developmental requirements and user feedback) and therefore it is likely that the finished application will be quite different from the initial design.

###### Goals
- Plan general system design in preparation of first sprint, including creation of initial system diagrams. &#x2705;
- Plan and design initial database structure. &#x2705;
- Create preliminary user-interface wireframes. &#x2705;

The overarching goal of the project is to design a website where users can import data from their surveys, create graphical visualisations and carry out statistical tests. The application will communicate with a database, saving information regarding that user, their diagrams and statistical tests. Data imported by the user will first need to be pre-processed on the server to identify any anomalies and to prepare data for creation of graphical visualisations. The creation of the data visualisations will happen on the client side (using javascript D3.js) whilst the calculations for statistical tests will happen on the server side. The results of both will be displayed to the client and can potentially also be exported.

<p align="center">
  <img src="diagrams/sequenceDiagram.png" />
</p>

In order to keep a record of the user's data, a database will be required. In the long term, there might be the option to also use the application as a 'guest' user and this will have to be incorporated into the system. However, for the time being I will design my database around having user accounts as this will make saving data (and identifying which data belongs to which user) much easier. The preliminary design will use 4 entity tables: User (containing account information such as email and password), Data (which contains the filename of the data in table form), Graph (which will contain information regarding the title, the variables plotted (as an array) and potentially information regarding x/y-axes) and StatisticalTest (containing information on which statistical test was used, and what the result is).

<p align="center">
  <img src="diagrams/preliminaryDatabaseDesign.png" />
</p>

The 'Graph' entity will likely raise some problems, as it can vary between the different types of graphs. For example, a line chart will need to know what is plotted on the x-axis and what is plotted on the y-axis (and possibly z-axis), whereas a pie chart does not have an axis, but could theoretically contain any number of variables. Fortunately, using a NoSQL database allows for some degree of flexibility in this, allowing for creation of different variations of a particular entity. It also allows for the use of an array which will be useful for storing multiple variable names.
However this preliminary database schema will likely need to be reviewed and redesigned at later stages in the project when implementing.

Some examples might be as follows:

<div style="display:flex; justify-content:center;">
  <img width="15%" src="images/UserTable.png" />
  <img width="15%" src="images/DataTable.png" />
  <img width="15%" src="images/StatisticalTestTable.png" />
  <img width="15%" src="images/GraphTable.png" />
</div>

##### Wireframes
The original wireframes have been constructed using [pencil project](https://pencil.evolus.vn/) and can be found in the [wireframes](week1/wireframes) folder inside week1.

### Early Implementation Log (Week 1)

For my python code I have chosen to follow the python style guide outlined by [PEP 8](https://www.python.org/dev/peps/pep-0008/#naming-conventions).
Following the initial installations and project design described above, I decided to experiment with creating a very basic web application which simply connects to a server and loads a few basic pages (following the UI design shown in the wireframes):

* A landing page (that simple has the title Survey App and a couple of links).
* A file upload page (non-functional, just simply getting familiar with the languages and framework).

It quickly became apparent that I would need to handle web forms and input from the user and this feature isn't natively built into the Flask framework.
I decided to install the flask extension [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/) which is a wrapper around the WTForms package.

```
pip install flask-wtf
```

This allowed for creation of web forms with some degree of input validation.

I also installed a [dropzone.js](https://flask-dropzone.readthedocs.io/en/latest/) extension to allow fo easy uploading of files by dragging and dropping.

```
pip install Flask-Dropzone
```

One way to keep a record of any uploaded files is to save the filename in a database associated with that user. To do this, it would require having user accounts and subsequently a registration and login page. I therefore decided to draft a login/registration page at this point of the project (and then at a later date I will return to handling 'guest' users, and how this information would be stored for these users without an account.) Again, at this stage these pages are non-functional (i.e. it does not actually register/save details entered into the form) but simply made for practice/experimentation and to get familiar with the language and tools.

For saving the information I will need to connect to a database. MongoDB is my chosen database for this project and it is possible to connect to this though a flask application using [Flask-PyMongo](https://flask-pymongo.readthedocs.io/en/latest/). It represents MongoDB documents as a repository of Python dictionaries.

```
pip install Flask-PyMongo
```

#### Project restructuring

During the early stages of experimenting and development of the application, I decided to carry out a restructure of my file system and code. This will help to keep my application more organised as it gets larger and will allow for easier testing.

I used the flask concept of [blueprints](https://flask.palletsprojects.com/en/1.1.x/blueprints/) which allows for modularisation of the application by creating 'sub-packages' in the application for each of the different sections. For example, for now I have created a 'users' package (which contains all routes relevant to users, such as login/registration), a 'main' package (which contains the 'index' route) and 'graphs' (which contains the 'import' route). I have also moved the login/registration forms ('forms.py') into the users package. If later I also have forms relating to graphs then I will create a 'forms.py' file inside the 'graphs' package. Each of these packages contains a '__init__.py' file (which is how python recognises these as packages. It is empty for the time being).

Further to this, I have decided to follow flask's [application factory design](https://flask.palletsprojects.com/en/1.1.x/patterns/appfactories/). This involves putting the creation/initialisation of the application into a function. This has a few benefits:
* First, it allows for creating multiple instances of the application (which will be useful for running different versions of the application with different configurations depending on the environment I am running the app in.)
* Secondly, it allows for unit testing of the application as I can effectively run instances of the application with different settings to test every case.

I have also separated out many of my configurations into their own class (inside a 'config.py' file) which can easily be imported and applied to my application. Any 'secret' variables, such as the application 'SECRET_KEY' (which is used by the application to give security against things such as Cross Site Request Forgery (CSRF)) and the database URI have been moved into a separate '.env' file which the application can access. I have also created a '.flaskenv' which contains some commands that can automate the running of the application.

```
FLASK_APP=survey.py
FLASK_ENV=development
```

This allows the application to be run simply using the command:

```
flask run
```
<a name="latestEntry"></a>
#### User Authentication

Authentication will be required in my application for user registration and logging in. This is so that users will be able to access their own personal 'dashboard' containing their previously made graphs/tests. The user will therefore need to have login details (an email address and password). The password in particular will need to be kept secure and to do this I will use bcrypt to hash the password before saving.

```
pip install flask-bcrypt
```

Another extension that can be very useful for managing user logins and authentication is Flask-Login. Using this extension allows me to handle things such as remembering user sessions over a period of time.

```
pip install flask-login
```
