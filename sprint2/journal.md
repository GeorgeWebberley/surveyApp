### Sprint 2 (starting 22nd June)

I have decided to move on to sprint 2 slightly earlier than anticipated (original plan in the proposal was to start sprint 2 on the 29th June). This is partly because I was able to start the project earlier than I planned but also because I have made good progress towards my objectives with the creation of a minimum viable product that would benefit from user feedback.

A summary of the user feedback can be found [here](../sprint1/journal.md#userFeedback1) at the end of sprint 1.

###### Goals
The overarching aim of sprint 2 is to review the minimum viable product with the user feedback from sprint 1 and the backlog of jobs needed to improve the application. More specifically, this will involve:

- Review system diagrams and database design and make any changes if necessary.
- Creating an export feature, allowing users to export their graph (and maybe also statistical test) as an image or pdf.
- Fixing any existing bugs, such as issue with loading javascript on the 'analyse' page. &#x2705;
- Minor changes, such as changing 'Dashboard' to 'Home', fixing case sensitivity on email login &#x2705;
- Add more choice of graphs and more statistical tests.
- Make site more responsive, so that it can be used on smaller screens such as iPad.
- Allow users to input their survey data directly, as opposed to importing a CSV/XL file.

### Review of sequence diagrams and database design (22nd June)
The 'sequence' diagram from sprint 1 is still very much valid, with only some minor changes needed. Previously I carried out the data pre-processing on the server side and sent the reduced data set needed for creating graphs to the client. However, as described in [this](../sprint1/journal.md#dynamicGraph) section, giving the user the ability to choose their variables and axes on the graph page and get instant visualisation would likely reduce traffic of the user having to go back and forth with the server to get the result they want. Therefore I have updated the sequence diagram to show how the data processing for graphs occurs mostly on the client side in D3.js.


<p align="center">
  <img src="../diagrams/sequenceDiagram2.png" />
</p>

The design for the database has changed also since the preliminary design. In the original design, graphs and statistical tests referenced the 'survey' entity which in turn referenced the 'user' entity. This has since changed, with graphs, tests and surveys all referencing the 'user' entity, with graphs and tests also referencing the 'survey' entity. I have updated my diagram to reflect this.


<p align="center">
  <img src="../diagrams/databaseDesign2.png" />
</p>

As discussed previously, this design is flexible, meaning that the design of the 'graph' entity will vary considerable depending on the type of graph being made (e.g. different numbers of variables, x/y axes, aggregations etc.) Furthermore, I also expect the 'test' entity to vary depending on the type of test. This is an advantage of using a document based database such as MongoDB. The python code will be able to check the 'type' of graph/statistical test and then know how to read it accordingly.


### Bug fixing (22nd June)

I explored the different possible reasons why the javascript file was not loading for one user when accessing the 'analyse' page for creating statistical tests. After some searching around on the internet, I realised that one possible reason could've been the use of an adblocker preventing some of the content being loaded. A lot of adblockers will identify any static files such as images, CSS and javascript files with 'suspicious' sounding names (names such as 'advert.jpg'). My javascript file for the analyse page was called 'analyse.js' which I thought could have been a culprit. I downloaded an adblocker extension to test it on my computer and discovered that changing the name from 'analyse.js' to 'statistic.js' solved the problem!

### Account edit (22nd June)

One comment was to allow for editing account details. I have therefore added an 'account' page where users can update their email, first name or last name. I will update this soon to allow users to also reset their password.

### Initial attempts at creating an editable table page (23rd June)

One of the comments in the user feedback was to create a way for users to manually input data, as opposed to importing it from a file. I thought that one way to do this nicely would be to create a mini excel-like table in the website where users can manually input data. This would also allow users to edit data in their uploaded files. To do this I looked at the javascript extension 'handsontable'. This allows me to render existing excel/csv files in table format.
To do this, the data has to first be converted to an object or 2d array on the server side. This can then be sent to the client javascript using flask and then rendered using client side javascript. To 'save' the changes, the javascript needs to 'post' the updated table back to the server using an AJAX post request.
So far, I have implemented editing a table. However this is still at an early stage and will need reviewing and updating as I go. Furthermore, I will need to work out how to allows users to make tables from scratch (i.e. adding rows and columns themselves, as opposed to editing rows/columns that already exist.)

To make this simpler, I may return to how the files are saved (currently they are saved as excel or csv files. However, I may change this so that all files are saved as CSV. This will make updating the files much easier as the information saved by 'handsontable' is typically in CSV format unless otherwise specified - which would be hacky to code as the client would need to know if it is Excel or CSV before sending it)

### Continued work on 'edit table' and 'new table' (24th June)

Today I have continued to try and get familiar with using handsontable as a tool for editing existing tables and for creating tables. I have now added features so that users can add more columns to the table with a column header for each, representing that variable/survey question.

I have also made it so that rows are automatically added (i.e. when the user enters in data in the final row a new row is automatically added on) and that any empty rows are not saved.

I have also began to work on the page also being able to start with an empty table, so that users can manually input data from scratch if they do not yet have an excel file or csv file.

The overall appearance of this page will still need reworking. Also presently, when the user is creating the table from scratch it does not yet save it to the database. This will be the next thing I work on before moving onto other issues highlighted from the user feedback.

### Finishing table edit page and redesigning home/dashboard (25th June)

Today I continued working on the 'edit' table page, allowing users to save their changes after editing their raw data, as well as being able to start a new survey/table from scratch and save this.
The saving of the table produced a few challenges. Predominantly it was with regards to sending the data back to the server via a POST request. All of my previous POST requests have been handled by WTForms, which carries out a pre-validation of the form on the server side, handles CSRF tokens and validates the return submission. However, as the table is completely built on the client side (using front end javascript and handsontable) it was difficult to think of a way to post this to the server whilst mainting security through the CSRF token. In the end, I used an AJAX call using JQuery. I extracted the CSRF token value from the WTForm (which also contained a 'title' field) and could factor this into the AJAX call.
On the server side, I was then able to extract the table data (sent in string form) and the 'title' data and carry out the appropriate save to the database.

I also changed the way I save files after a user uploads. Now, all files are converted to CSV (using pandas) before saving, which allows for easier handling at later stages.

I am also working on changing the home/dashboard. One user feedback comment said how it would be nicer if the home/dashboard is survey-centric (i.e. the user selects a survey and the dashboard focuses on that, with graphs and statistical tests from that specific survey.) Whilst this is now functional, the appearance is not quite right and will need modifying (e.g. buttons different sizes etc.). Furthermore, I am beginning to find that much of my original code (such as CSS classes) is now obsolete. I will need to spend a day in the near future refactoring code, deleting obsolete code and making my code DRY.

### Frustrating progress (26th June)

Today I wanted to continue working through the feedback comments from the users. One such comment was about making the pages responsive, so that they work on smaller screens. For this I decided to try and integrate some of the bootstrap classes. I have not used bootstrap before, and whilst it started ok on the index page, many of the classes clashed with classes i had personally made, causing many other pages to work incorrectly. Furthermore, many of my javascript functions are already linked with the classes I have been using and therefore removing/changing these affected many of my javascript functions. After spending the morning trying to fix it, I decided that it was likely going to take quite some time to get familiar with bootstrap and integrating it into my application. There are many other pressing matters that need sorting on my application (such as adding more graphs, more statistical tests etc.) that should likely be prioritised first, so i reverted back to a previous git commit and will come back to look at making my pages responsive at a later date when I feel I have more time.

Another comment was about making the dashboard easier to read by providing small images for each graph (as opposed to simply the title of each graph). I spent several hours this afternoon attempting to convert the D3 SVG to jpg/png and then to post this to the server but to no avail. Furthermore, I found that through changing my javascript files to try and do this resulted in many of my old/working javascript functions failing. I think that this method (of first converting to jpg on client side before posting) comes with problems and instead a better route may be simply to render the D3 SVGs themselves on the dashboard, although this would require a lot more data traffic being sent to the client. I will need to think about the pros and cons before coming to a decision.

Overall, it was quite a problematic day, with very little achieved. I hope that soon I will be able to solve some of these problems, or instead I may need to move straight on to adding more graphs/statistical tests with limited time being a factor.

### Improved responsiveness and saving images(27th June)

Following on from yesterday, I continued working on the responsiveness and also on saving images to the server of the graphs produced.
I realised today that the problems I was having were with the firefox browser. When saving the images using chrome or safari I had no problems. This is something to do with the way that firefox codes the canvas to data URL.
Furthermore, the responsiveness of the graphs on screen resizing that I worked on yesterday only seemed to work on firefox. I have now fixed this so that it works on chrome and safari too.

I have slowly started to reintegrate some bootstrap classes. I have made my navbar responsive using some bootstrap classes (navbar links collapsing into a menu) and have now placed my graphs inside bootstrap grid systems which helped improve responsiveness.

Tomorrow I will finish off the image 'saving' and also presenting small image 'cards' of each graph on the dashboard. I will then crack on with adding more graphs and statistical tests on Monday (if all goes according to plan!)

### Image cards on desktop(28th June)

Today I finished making the image 'cards' on the desktop. For this, I used bootstrap 'cards' which allow for making nicer contained elements with a picture, small amount of text (in my case the title) and also for buttons (edit button and delete button).

From tomorrow I will work at adding another graph/statistical test to the application.

### Altered landing page and finished graph cards (29th-30th June)

Today I worked at improving the landing page for visitors. I have added a background image (which I will likely change in the near future) as the previous landing page was very bare with very little content.

The cards which display the users graphs have been finalised with buttons for editing and deleting.

### Altered landing page and finished graph cards (1st July)

I have altered the statistical page data (as the dashboard is now centered around one survey, so i no longer need to ask the user which survey they would like to use).

I have worked at adding a 'scatter plot' type of chart. Whilst I was able to do this without too many difficulties, the problem I am now experiencing is with regards to how to structure my code and to organise it with the different types of graphs. Initially I made different HTML pages, different routes and different javascripts for each of the different graph types. I have now tried to reduce the number of different routes, with one single 'graph' route which will process the graphs depending on what type of chart. Whilst this is almost working, the server is generating an error when trying to edit a graph (as it does not know which type of graph it is). I will continue working on this tomorrow, as I feel it is quite an important thing to get right in my project.

### Line graph, value ranges, negative graph values, graph edits (2nd July)

This morning I was able to fix a bug that was not allowing the graphs to be edited (this was introduced yesterday when I condensed the two different graph routes (scatter and bar) down to one route that calls different functions depending on the graph type). Although it is now working, i am still not really happy with my code. This is because there are lots of small differences between bar charts and line graphs, meaning that most of the code is 'similar' but very slightly different, making it difficult to prevent the code seeming to repeatable. This will be a problem I will likely continue to face as I add more graphs and statistical tests.

I decided today to also add a line chart. After starting it, however, I soon realised that it is very similar the scatter chart made yesterday (in fact it is the same, just with a connecting line). Therefore, I decided to combine the the graphs together and simply having a 'scatter graph' but with an optional extra check box that the user can tick if they want to connect their points with a line.

For a while I have wanted to give the user the opportunity to set their own ranges in their graphs (this is called the 'domain' in D3). I have therefore added some extra input boxes where the users can specify upper and lower bounds for their graphs. I have also adjusted the axes, fixing them to the 0 value when needed.

The next thing to add here will be to save these extra features to the database (the line and the ranges). I then want to maybe create one more chart (a pie chart perhaps) before adding more statistical tests.

Following having more statistical tests, I then want to work at improving the current graphs (such as making them interactive, zooming in on sections etc.)


### Attempt at pie chart (3rd July)

I have now expanded on the database design for scatter charts, so that it can now save information regarding the ranges specified by the user, as well as whether or not they want to add a line to their chart.

I have began a page to render pie charts for the user. Whilst this is similar to bar charts (in the way that the data has to be aggregated before hand) it is very different in terms of rendering the SVG. I have now managed to get it working, however adding the labels has proven to be difficult (as labels are of varying sizes and therefore their anchors need to be varying distances from the pie chart). I will continue to work on this tomorrow. If i continue to struggle then I may instead attempt to use a legend instead.

### Finish pie chart (preliminary) and adding more statistical tests. (4th July)

I have finished up with working on the pie chart for the time being, by adding a title to the graph and correcting the variable names. I have also corrected a bug where the image was not saving when attempting to save a pie chart (to do with how the SVG was formed).

I have started working at adding more statistical tests (Mann whitney U test). At the moment I am finding it hard to work out how to guide users through this stage. Initially, I wanted to be able to suggest statistical tests to users based on the types of variables (or visa versa, to limit the types of variables presented to the user after they select a type of test). However, whilst some data types can be easily calculated (i.e. numerical vs non-numerical) others cannot (such as a likert scale, usually presented from 1-5 should be treated as categorical rather than continuous data). Instead, what I may do for the time being is simply give users the options to select any variable/test combination but guide them through the process (e.g. when they pick a statistical test, information is presented to the user regarding what type of independent/dependent variables they should pick).

### Adding statistical tests. (5th July)

I have added chi square statistical test and also Mann Whitney U test. The server can now compute the answers to these tests, using Pengouin and Scipy. I have also corrected the javascript on this page which contained a few bugs.

I have added tooltips which will guide the user through selecting their test and the correct variables. I have added some validators that check the user has selected the correct variable types for the specific tests.

Tomorrow I will add some more tests commonly used in surveys. Then I will spend a few days reviewing my code, refactoring and also reviewing the user interface.

<a name="latestEntry"></a>
### Difficulties adding more tests. (6th July)

I am finding that as my application grows bigger, it is very difficult to integrate new features that are similar but slightly different from existing features. This is particularly apparent with the statistical tests.

Many statistical tests have similar features (such as needing a variable, producing a p-value) but have minor differences. For example, some take 1 independent and 1 dependent variable, some just take 2 variables in general, some take one variable. Also, some tests take additional information (such as chi goodness of fit which also needs to take input from the user regarding the expected distribution of categories). It is very difficult to not make the code repetitive. Either I have to make separate routes and HTML pages for each (which can make the code very repetitive) or I have to try and factor all the differences in to single routes/templates that can account for all the minor changes (which often results in lots of if-statements to check what is needed). This will likely be a problem as I continue to expand on my project.

##### Ongoing objectives

* Add more statistical tests.
* To carry out unit testing of the graph page, statistics page and dashboard pages.
* Password reset.
