## Sprint 1

#### Goals:

The overarching aim of sprint 1 is to produce a working minimum viable product (MVP).
This can be broken down more specifically into the following goals.

* Create a web application that runs on a server, loads some basic pages and connects to a database.
* Get familiar with the tools being used for the web application (python, flask, D3.js, MongoDB).
* To create some sort of way for users to input data (through upload or direct input).
* Display the data in tabular form.
* Create a basic graphical visualisation using sample data.

### Early Implementation Log (Weeks 1-2)

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
<a name="factory"></a>
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

I have also now installed pytest so that I can carry out unit testing of my application. These tests can be found inside 'test_surveyapp.py'.
It actually took a considerable amount of time to work out how test can be carried out on an application such as this. A lot of the documentation online is not for flask applications and the ones that are required a lot of altering to get them to work.
The 'test_surveyapp.py' file creates an instantiation of the application object (as discussed [above](#factory) in the application factory design) and applies my test configurations to it (as seen in the config.py file) by using the following line of code:
```
app = create_app("test")
```
as opposed to the instantiation created whilst I am developing:
```
app = create_app("dev")
```

The tests can be run simply by running the command:
```
pytest
```
Despite the project restructuring and automated testing taking a while to setup, I am glad I have put the time in now to do it as it will certainly make my life easier going forwards. It is now very simple to add further tests to my application and the current application structure (modularised with blueprints) will help keep the application organised as it grows.


#### User Authentication

Authentication will be required in my application for user registration and logging in. This is so that users will be able to access their own personal 'dashboard' containing their previously made graphs/tests. The user will therefore need to have login details (an email address and password). The password in particular will need to be kept secure and to do this I will use bcrypt to hash the password before saving.

```
pip install flask-bcrypt
```

Another extension that can be very useful for managing user logins and authentication is Flask-Login. Using this extension allows me to handle things such as remembering user sessions over a period of time.

```
pip install flask-login
```

#### Displaying data in tabular form

From researching different packages, I have initially decided to try using pandas to display uploaded files in tabular form (and also xlrd which allows for excel support also).

```
pip install pandas
pip install xlrd
```

I initially experimented with displaying an 'editable' table, so that the user could review their data and make any changes if necessary. This would also be useful for later when I implement data cleaning functions, as I will be able to highlight any anomalies to the user (such as empty cells) and the user can make changes directly into the data. To do this I created a dynamic form element in HTML, made up of multiple 'textarea' inputs to make a grid that resembles a table. Whilst this worked well, looping through the panda dataframe (to populate each cell of the table) was not very efficient, taking up to 5-10 seconds to load the web page. Whilst this is not a catastrophe, I feel that it could certainly be improved on. The HTML for this attempt is in the [table.html](../site/surveyapp/templates/table.html) file.

Another way to display the data very easily and quickly is to use inbuilt pandas function 'df.to_html()' which converts the loaded excel/scv file straight into HTML. The downside to this is that the data cannot be manipulated as it can in the other method I tried. The advantage is that it is much faster and therefore probably more appropriate for my MVP. The HTML for this is in [table2.html](../site/surveyapp/templates/table2.html). Later, when I implement data cleaning, I will look to see if I can use the 'forms' method.

#### Displaying a basic graph

To get familiar with using D3.js, I have decided to try making a bar chart of some pre-set data. This is by no means dynamic, as I am directly using the variable names to define my axes and therefore it can only be used for a specific data set. I decided to use a very basic CSV file which contained 10 countries and their population numbers.
pandas could be used to parse the CSV file (using 'pd.read_csv(<filename>)') and then convert this to a json file which resembles a list of dicts (e.g. [ { country: "China", population: 1415046 }, { country: "India", population: 1354052 }...] }). I then used javascript and D3.js to plot these 2 variables against eachother on a bar chart. Obviously, this is quite different to processing survey data, as most survey data first requires aggregation.

#### Making bar chart compatable with other data

The chart I made for population.csv was hard coded into the javascript (i.e. I knew the names of the table columns so I could apply those directly). Furthermore, the data in that file does not need to be aggregated, as is the case with most survey data. Firstly, to aggregate data, I used some built in functions in the pandas library. Those are the groupBy function (similar to SQL GROUP BY) and the agg function (which allows for carrying out aggregation, such as summing, averaging or counting). The most useful of these these with regards to survey data is 'count' as survey data often comprises of many different individuals responses that should all be counted together before meaninful conclusions can be drawn. I created an example survey data set which had 10 respondents all choosing their favourite flavour of icecream (chocolate, strawberry or vanilla). These 10 responses were aggregated, with 5 choosing chocolate, 3 vanilla and 2 strawberry. I was then able to apply this newly aggregated data to a bar chart to display the results.
Further to this, I removed the hard-coded column headings and made it so that the user can choose a column heading, which is passed to D3.js which then uses a function to populate the bar chart dynamically.

#### Restructuring download/Setup

Initially in my [documentation.md](../documentation.md) I had instructions for how a user can install each of the individual python packages being used. I have now changed this, so that anyone downloading the repo can instead just install the python package [pipenv](https://pypi.org/project/pipenv/) which will handle the virtual environment and also carry out all the relevant package installations. I have kept the old instructions in place in case a user wants to still install packages individually.


#### Saving graphs (11th June)
I have now implemented a feature so that a bar chart can be saved along with its respective title. This is then present on the user's 'dashboard', where they can view, edit or delete their graphs. Furthermore I have implemented the feature to delete the survey data files. Doing so will also delete all respective graphs relating to that file.

#### Difficulties designing application (11th June)
As my application develops more and more I am finding that the code is getting a bit more disorganised/messy/reptitive. I anticipate soon I will need to refactor my code to improve readability and efficiency.
Furthermore, I am finding it difficult to plan how I will go forwards with statistical analysis and graphs. At present, the application is able to produce a bar chart from one variable. However, users may want to factor in multiple variables into their charts. Furthermore, users may want to analyse their data first (for example, obtain averages) and then graph the results of these sums. I will be developing these features into my application over the coming days.

#### Quick Stats Page (12th June)
I decided to make a page which can display a set selection of basic statistics to the user depending on the type of data being used. For example, categorical data (such as words) is not averaged or summed, but instead grouped and counted, and gives the user details of the most and least commonly occurring answers. Numerical data (such as age) is averaged, as well as providing the user with the maximum and minimum values. These stats will also be useful later when it comes to creating graphs.

I presented this to the user in a grid format. It took a while to get the css that I wanted, particularly when some columns are very long and some are very short. To get round this I used the JQuery package [Masonry](https://masonry.desandro.com/) which allows for dynamic grids.


#### Dynamic javascript graph generation (13th June)
One thing that I thought would improve the user experience would be to have the graph criteria (such as what variables are plotted on what axes) as selectable options on the actual graph page itself. Therefore, I have slightly restructured my application so that a lot of the data is sent to the client when they open the graph page. Javascript is then used to dynamically create the graph as the user selects options in drop down lists. I think this improves the user experience as it allows the user to try different options and get immediate results rather than having to reload the page. At present, I have only done a single variable (the x-axis on a bar chart) but will eventually allow for more settings.

The downside to this approach is that all the data has to be sent to the client when they load the page, even if the user only plans to use a small amount of that data. This will obviously have the potential to add unnecessary traffic between the client and the server. However, I think that overall it may in fact reduce overall traffic instead, as the user is immediately able to see the result of the graphs and play around with the settings without having to communicate back and forth with the server to get the graph that they want.

#### More settings for bar chart (14th June)
Before finishing up on the bar-chart for sprint 1, I wanted to give the user more settings to plot their bar chart against. Currently, the user is able to select a variable for the X-axis (e.g. 'Favourite ice-cream') and then a chart is created using the 'count' of that variable (e.g. 5 people chose chocolate, 8 chose strawberry etc.).

However, it is very likely that a user would want to get more information out of their data. For example, they may want to know the average age of people who chose chocolate compared with the average age of those who chose strawberry. I have therefore implemented features that allow the user to pick a variable for their y-axis and how they want the data to be aggregated (the x-axis variables are grouped, and therefore the y-axis has to be some sort of numerical aggregation, such as mean, sum etc.). Furthermore, I have limited the variables that the user can pick for their y-axis to only numerical values. Y-axis on a bar chart has to have some sort of numerical value and therefore it is not possible to plot a categorical variable which has no value (such as true/false or 'Favourite ice-cream').

All of this aggregation was done using D3.js which I have found to be easier to use and get familiar with than using Pandas. Furthermore, it can all be done on the client side, reducing back and forth communication with the server (as discussed above).

<a name="latestEntry"></a>
#### Exploring D3 more with regards to enter, update and exit (15th June)
I spent some time trying to really get familiar with D3 as it is a core part of my project. I followed many tutorials to get to grips with the concept of 'enter', 'update' and 'exit'. One big problem is that many people and tutorials still use version 3 of D3.js, which is very different from the most recent version (version 4).
Understanding these concepts has allowed me to better 'bind' my data to the DOM elements. Previously, each time the graph changed I would clear/delete the graph and redraw it. Now I edit the previous DOM elements, add new ones if needed and delete ones no longer being used. This allows for improved manipulation of the DOM elements, such as using transitions.
I have subsequently altered my bar-char page to include transitions as the data changes. I have also moved all the axis settings on to the left of the page for easier access.

I will want to now work on getting some basic statistical tests done, so that I have covered all aspects of my project in a basic way before getting user feedback.

##### Ongoing objectives

* Now that the way the graph is made has changed, I will need to review the way the server saves and stores graphs in the database.
* To start thinking about getting user feedback so far.
* Add more graphs. I think line graph would be a good next one to look at as it will be quite different to bar charts. Pie-charts I think will be quite similar to bar-charts as it is mostly categorical data and aggregations, only the presentation is different.
* To carry out unit testing of the bar-chart and dashboard pages.
