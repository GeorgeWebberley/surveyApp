### Sprint 3 (starting 13th July)

It has been three weeks since the start of sprint 2. The total changes made over sprint 2 can be seen in my [sprint 2 journal](../sprint2/journal.md) but are summarised below:

- Two new graph types have been added to the application (a scatter chart, with an option to display as a line chart, and a pie chart).
- 3 new statistical tests have been added (Mann-Whitney U test, Chi squared test and Chi squared goodness of fit test)
- Big changes made to the user interface compared to sprint 1, integrating in Bootstrap CSS and javascript and improving the responsiveness so that it can be used on smaller screens.
- Export feature has been added - users can download their graphs as images to their devices to be used outside the app.
- Quick stats page where users can get a quick overview of their data without having to analyse it themselves.
- Manual data input - users can now input data in table form (similarly to Excel) so that they do not need to have a file that they upload. Users can also edit their uploaded files in this way.
- I have made a small demonstration video that users can find on the index/landing page.
- I have obtained a domain name (datasaur.dev) and have cloud hosted the website on Digital Ocean under a user with reduced privileges. I have also now installed Nginx on this server and use it to deliver my static files, improving responsiveness.
- I have secured my website with an SSL/TLS certificate and redirect all users from the HTTP version of the site to the HTTPS secure version.
- Improved account features: registration, login, validation/security checks, account update and password reset by email.

User feedback from sprint 2 is still being returned, but some of the key points so far include:
- Adding a histogram type chart.
- Adding more tests/graph types.
- Allowing for date/time on the scatter chart.

###### Goals
Sprint 3 will be the final sprint of the project. Therefore most of the final development will occur over the next 3 weeks. Following this sprint, I will be making only minor changes/bug fixes and refactoring the code. The overarching aim of sprint 3 is to review the existing application with the user feedback from sprint 2 and the backlog of jobs from sprint 1 and 2. I plan to refactor the code, add more features (such as graphs/statistical tests) and then to get some final user feedback on the project.

More specifically, this will involve:

- Review system diagrams and database design and make any changes if necessary.
- Adding a histogram graph type.
- Adding date/time to scatter chart/line chart.
- Adding some more commonly used statistical tests in survey data analysis.
- Reviewing existing code and refactoring any repetitive code.
- Develop a 10-question feedback form to get more detailed feedback on the final application.

### Review of sequence diagrams and database design (13th July)
Little has changed in the general system architecture of the project since the previous sprint. The sequence diagram is still very much the same, with the processing of data for graphs still being carried out by D3 on the front end, as I think that overall gives the user the best experience, despite the downside of any unused data also being sent to the client. The processing of data for statistical tests occurs on the server side, although some javascript functions are also used on the client side, to populate the pages with advice/information regarding different statistical tests.

<p align="center">
  <img src="../diagrams/sequenceDiagram2.png" />
</p>

Likewise, the design for the database has changed very little since the previous sprint. The only additional thing I am findings is that each test and graph will have different characteristics that need saving. This is more apparent than I initially thought, with nearly every type of graph and statistical test requiring its own document structure in the database.

<p align="center">
  <img src="../diagrams/databaseDesign2.png" />
</p>



### Unit testing and adding histogram. (14th July)

For a while I have wanted to carry out some more substantial testing of my pages. Using Pytest, I spent the morning testing existing pages, including import/file upload and creating statistical tests and saving them.

I am finding some difficulties with regards to testing the 'data input' page. This is because of the way that Handsontable saves the data being input into the cells which is difficult to replicate in simple post requests in pytest. Likewise, currently I am struggling to find a way to test saving graphs, as in the application an image is created of the graph SVG and converted to data URI to be transported to the server, a behaviour that is again difficult to test with pytest functions.

I have spent the afternoon making a start on the Histogram page. One difficulty I am experiencing with this is what options to give the user. A histogram is generally made up of grouped numerical data, representing a spread/distribution of that data. Therefore it should only really take one variable - the x-axis that the user would like to see the distribution of. However, a user may also want to customise the histogram in other ways, such as deciding on their own bin sizes or number of bins ('bin' here means the groups of data. For example, bins of Ages may be 0-9 years, 10-19 years, 20-29 years etc.). Not all user choices are possible, for example if the scale on the x-axis is from 0-20, then having 11 bins would not be possible. This is something I will continue to work on over the next few days. Likewise, as with the scatter chart, a user may want to choose their ranges on their x-axis which I have now enabled.

### Finished Histogram and attempts at parsing date/time. (15th July)

In the morning I managed to finish making a histogram. I tried to decide whether to add a line of best fit to the graph, so that it could give the user a good idea about the type of distribution (e.g. normal, positively skewed etc.). In the end I found that generally the histograms would display this distribution quite nicely even without adding the line, and in fact the line would quite often not represent well the apparent distribution anyway.

I spent the afternoon attempting to parse date/time. Whilst I have managed to achieve this on the server end, converting multiple different formats into Timestamp objects, it is difficult to convert this data into data that javascript can read. For example, javascript does not recognise the 'Timestamp' keyword in the data and subsequently raises an error. I will continue with this tomorrow before moving on to other matters.

### Tooltips and autostats. (16th July)

Some more user feedback came back today. It was all very positive which is nice to see! Something that came up a couple of times was to give some information regarding the statistical test and what certain things mean (e.g. significance value, null hypothesis etc.)
I have therefore added some descriptive text whenever a user selects a statistical test to run. When results are given, I have added tooltips that display the meaning of different technical terms, such as the ones mentioned above.

Something that I have planned to do for a while (and was suggested in feedback from sprint 1) was to run some 'auto' tests. This feedback was from a user who did not understand statistical tests but said they would find it helpful if the application ran some tests for them automatically.
I have started implementing some functions that will scan through the data when it is first uploaded and carry out statistical tests based on the type of data (numerical vs categorical). This obviously has some limitations and will not run all different tests on all the data (for example, non-parametric tests will only be run on definite categorical data - i.e. data that is string, object or boolean. Ordinal data with numeric values, such as likert scale, will not be tested as this data will be identified as numeric.) Furthermore, the results of tests will have to be checked by the user, to check the data passes the assumptions of the test. I plan to provide the user with the assumptions that the test makes so that they can check their data against them.

I do not perform mann whitney U and kruskal wallis on the same variables, even though it is in fact possible to perform kruskal wallis on 2 variables. This is to avoid conflicting results and subsequent increasing risk of false positives.

Any significant findings will be stored in the data base under a 'temp_results' collection. If any data is in the 'temp_results' then the user will be notified and they will have the opportunity to check it, save it (to go to their 'tests' collection) or delete it.

I am in the process of creating an HTML page that will render these features.

Depending on how long the scan takes, I may consider integrating 'threading' into my application, to handle this automatic scan in the background.

### Finished autostats. (17th July)

Today I finalised the 'auto-stats' page, rendering the different statistical tests that had significant findings. Each stat is presented with a list of assumptions that the user can check. If they want to save the stat, they can (with a custom title or an autogenerated title). This will then be saved in the 'tests' database so the user can access it from their dashboard. The user also has the option to delete/reject the finding.

### Getting user feedback and minor bug fixes. (19th - 22nd July)

I went home to see family for a long weekend. I spent some time going through the application with them, getting them to test various aspects and to get some user feedback. This was very useful, as I could watch them in person testing the application, so I could see where they would get stuck when using the app.
I found that on the whole, after uploading a file, the user would get stuck on the home page and not now how to proceed to make a graph (I have some text saying 'view graphs and tests' but this was obviously not clear to the user.) I will therefore work at changing this.

It was also insightful as many of my family wanted to test the application with massive documents, something that the server does not allow. I will therefore increase the file size to allow up to 10mb (currently at 5mb).

Some of their data sets contained anomalies, and therefore if time allows I would want to look into providing a data cleaning feature that scans their data and highlights any possible anomalies. This may have to be an extension due to limited time remaining with this project.

One final point was that uploading the large files often took some time, as my application scans them and automatically runs statistical tests on their data. This was not a problem with my test files, however with larger files it could take longer than 30 seconds. I will therefore introduce threading into my application, allowing this scan to be carried out in the background and then to alert the user when the scan is complete.

### Threading and statistical tests. (23rd July)

Today I introduced threading into the application to allow the scanning of data for auto-tests to be carried out in the background. Initially this raised a few problems. The main one being that the thread would not have the same application context of the main application. This means that all of the initialisation of the application (the configurations) as well as certain variables (current_user, current_app) could not be used. To get round this problem, it is possible to specify the app_context from within the thread. I passed the application 'object' to the threading function and then run a command:

```
with app.app_context():
    #do something
```

This then allows me to access current_user and also the database from inside the thread.

I also spent some time reviewing the statistical tests, trying to make them more specific to the data. For example, some tests require a certain sample size (chi square independence requires that 80% of the 'groups' inside the chosen variable contain more than a count of 5). Adding in these extra checks has increased my code, but has reduced the number of statistical tests carried out unnecessarily.


### Correcting statistical tests and starting data cleaning. (24th July)

I realised this morning that some of the results obtained from the Chi-square goodness of fit test were incorrect. The way my function was currently setup was to calculate the percentage frequency of each group in the column and compare this with the expected percentage (i.e. if 5 Males and 15 Females, my program converted this to 25% males and 75% females). This is clearly incorrect, because even though the ratios are the same, the size of the group will also have an impact on the result (e.g. 250 Males and 750 Females is quite clearly more significant, despite the same ratio). I have therefore corrected this in my code.

I have also added a 'delete all' button on the notifications page. This is because, when surveys are very large (with 50+ columns) then there is potential for there to be a very large amount of significant findings. It is very manual for the user to have to delete these one at a time and therefore adding a delete all button will hopefully make this easier.

I have began working on some basic data cleaning. I have added functions that will remove empty rows or empty columns from the beginning of a dataset (some users do not start their tables on the first column/row on an excel spreadsheet and therefore the program should account for that). I have also added in a function that will automatically trim leading and trailing white spaces in any "string" data. I considered also automatically converting the cells to upper or lower case, however this may be something that the user wants to keep separate (for example, they may want to use 'a' and 'A' as different results and therefore would not want automatic conversion). I may decide to add a button that will convert the case for the user if they wish. These entries (as with the leading and trailing white spaces mentioned previously) are read as separate values and therefore can create some confusion for the user when they attempt to make graphs and see that multiple variables are displayed instead of just one.

Lastly, adding some sort of spell checker may be useful for the user, although again I think this should be a manual function instead of being carried out automatically (as a user may wish to have 2 variables, both with similar names, but to be treated differently.) I will continue to work on this over the weekend.


### Fixing CSS and attempting more data cleaning. (25th July)

One of the pages that has not been responsive for a while was the quickstats page. This page was a grid made up of 4 columns, which worked well on a large page but on a smaller screen size the columns would squash up width ways.
I have corrected this by adding @media screen size functions to the CSS, adjusting the width based on screen size. I initially attempted with bootstrap grids, and although Masonry (Javascript library being used for dynamic grid) says it supports bootstrap, I could not get it to work.

I have also added standard deviation as a stat as this is likely useful for users.

I have attempted to add further data cleaning functions. I want to be able to identify if there are columns with potential typos (e.g. a letter in a column which is otherwise filled with numbers, or an obvious typo in a string column.) This has proved to be much more difficult than anticipated. None of the in built pandas functions seem to be able to identify columns of "mixed" data types. I tried using the [infer_dtype() function](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.api.types.infer_dtype.html) but when testing on data with mixed number/string types it consistently just gave the answer "string", making it impossible to identify it compared to actual string type columns.
With regards to typos, it seems that it will be a large task in itself to recognise unintentional spelling mistakes in data and I would likely use up the last of my remaining time working on the project to solve it. Instead I might put it further down in my list of jobs and only return to it if I find I have excess time at the end of my project.


### Map data. (26th July)

One comment from a user was whether it would be possible to create a data map, representing countries that respondents are from. This was something I have wanted to try doing for a while but wasn't sure how to start.

From researching online, I found the package [Datamap](https://datamaps.github.io/) which is an extension of D3 and helps in the creation of such maps. However most of the information regarding it online is with regards to maps where you know the data in advance and therefore it took quite some time to fully understand how I could use it.

Datamap requires D3 version 3 unfortunately, whilst the rest of my application is built around version 5. I initially included just the version 3 script on the HTML page in which I will be making the map, however many of the functions between version 3  and version 5 have the same name but operate differently, causing conflicts with the file linked in my 'layouts' html (version 5). I therefore had to move the script for version 5 onto each of the HTML pages individually for the other graph types, so that I could include version 3 only on the map HTML. I will look to see if I can improve this code as having to repeat it accross multiple files does not seem like good practice to me.

Another difficulty I encountered was converting the Country names to ISO. Datamap requires that country data is supplied in ISO 3 character format ("GBR" for "Great Britain"). Initially there did not seem to be an online converted tool and I thought I would have to create my own manually. Finally I managed to create a function using some of the in built functions in datamap that solved this problem.

One final problem I am encountering is how to save the image. My save function currently is aimed at D3 svg nodes and does not seem to work on the map SVG. I will continue to try and figure this out tomorrow. I also want to add further functionality so that users can select to zoom in on certain parts of the map (such as Europe if all your data is in Europe). This functionality is almost working but will need to be extended to work for all continents.

### Finishing data map, sorting of tabular data and simplifying code. (27th July)

This morning I finished up on getting the data map page to work and exporting the SVG. The difficulty was with getting the svg.node() element so that it could be drawn on a canvas and making this reproducible so the same code could be used across all of my graph types.

I have added the other continents to the datamap, as well as adding a map displaying the different states of USA, so that a user can instead use this instead of countries if they wish. I have also altered the colour scheme and made a tooltip that displays the country as well as the values associated with that country.

One comment from a family member when I went home was that it would be nice to be able to sort the data in the data table (on the input page). This is so they could sort numbers ascending or descending order, so that they can see the highest and lowest values, as well as being able to sort words alphabetically. I have now added this feature to the handsontable, meaning that users can simply click on a column heading, causing it to sort without changing the underlying data.

Lastly, I have wanted to clean my HTML code for my graphs for a while. This is because many of the HTML elements were repeated between the files (such as the title, the export button), the graph section itself etc.) The main difference between the files is the axis/variable settings.
I have therefore created a 'graphs.html' template which the other HTML files inherit from. The individual graph type HTML files now only contain the code for the axis/variable input section, as well as the javascript files specific to that graph type. All of the other code has been moved to the shared graph.html file.

Additionally to this, I have also separated out the function which converts the SVG to an image and posts this with the other form data to the server when the user clicks the 'save' button. I have put this in it's own javascript file which I have included in the template 'graph.html' file so as to reduce reptitive code.

As I am nearing the end of sprint 3 (the final sprint) and most of the features that I intended to add have been done, I will likely spend the next few days reviewing my code in a similar way and refactoring it. There are also some small changes to make, such as increasing the file size allowance and making the home page more intuitive.


### Reorganising static folder and templates and adding tooltips. (28th July)

Today I carried out a big restructuring of my application. Previously, all of my routes relating to anything to do with surveys were in a 'graphs' folder. All of the utils relating to surveys and stats were also in this folder. The routes file itself was very large with many routes and functions, as were the 'utility' helper functions in graphs.utils.py.

In order to make this more organised, I divided these functions and routes into 3 separate python packages. 'graphs', 'surveys' and 'analysis'. Blueprints were create and initialised for each one and __init__.py files made (needed to  tell python this is a package). I created a 'routes.py', 'utils.py', and 'forms.py' file in each one and separated out the functions into the corresponding places. This has helped reduce the size of many files and made it much easier to read and manage.

Additionally to this I have also restructured the 'tempaltes' folder. Previously, this was a folder that just contained all of the html files without an sort of structure or organisation. I have now made multiple sub folders (users, graphs, surveys, analysis and main) and have put the relevant html files into each one.

In a similar manner, I have restructured my static folder, creating subfolders for different types of javascript files, as well as making a general images folder that contains subfolders for the site images and the images relating to the user's uploaded graphs.

I went through the old CSS file, removing and simplify any previous CSS classes (I want to continue simplifying this over the next few days.)

I have added some tooltips the the 'histogram' and 'scatterchart' pages. This was because they do not give the user the option to display anything but numerical data (as both of these graph types require numerical data) - the downside of this is that if the user has no numerical columns then there are no options in the select field. A small tooltip is created for this situation to explain to the user why this is the case so that they do not get confused.

### No internet - code refactoring. (29th July)

Unfortunately this morning there was a power outage affecting all of the flats in the building. Since the power came back the internet has been non functional and we have been waiting all day for an engineer to arrive and diagnose/fix the problem.

I started working on adding a box and whisker plot diagram (at the request of a user) but soon realised that this would be impossible to test without the internet. This is because the CSS and also many of the javascripts (including the ones for the D3 functions) are direct links to the CDN and therefore do not work without the internet.

Instead I have spent the day attempting to refactor code. Whilst this has been ok, it is also somewhat difficult as I am unable to test whether the changes I have made with refactoring have introduce bugs into the rendering of the graphs. Whilst I am fairly confident that it should be ok, I am slightly hesitant about changing my code too much without being able to test that it actually still works.

An engineer will be arriving at the building tonight and therefore hopefully tomorrow the internet will be back up and running so that I can make an attempt at creating a box and whisker graph.

### Finishing box and whisker. (30th July)

Today the internet was working so I was able to continue working on the box and whisker charts.
At first, there were several bugs in my code, introduced during the refactoring I did yesterday without being able to test it. I have now fixed many of these bugs but will continue to test the features of the application over the coming days.

The box and whisker plot itself presented a few challenges:
1. What will the user want to plot? Would they choose a single numerical variable for the y-axis, (such as 'Age') and then plot this for the entire survey? Or would they want to also plot it against a categorical variable (such as 'Gender') so that they can see the distribution across different genders and compare them?
2. How to present the whiskers? Traditionally the whiskers themselves could represent the highest and lowest values in the data. However, sometimes they can also be used to show other data (another commonly used one is showing 1.5 times the IQR above and below the first and third quartiles.) Wikipedia lists 4 features that the whiskers could represent.
* the minimum and maximum of all of the data (as in figure 2)
* one standard deviation above and below the mean of the data
* the 9th percentile and the 91st percentile
* the 2nd percentile and the 98th percentile.
I decided in the end to simply plot it as the highest and lowest values as this is commonly used in other graphing applications, such as Excel.
3. All the previous graphs usually have a single graph element displaying just one value. A box and whisker plot however displays much more data (the max, the min, the median, the first quartile, third quartile and interquartile range). It is therefore difficult to know how to display the tooltip. In the end, I decided to display the user all of this data upon hovering over the 'box' section of the graph.

Now that this graph is complete, I will carry out final testing and final reformatting of code before focussing on the dissertation write up.

### Redesign home page, analysis page, results page and refactoring code. (31st July)

One of the user comments was to make the home page more intuitive. In fact, this was something I saw in person too when watching my family members test out the application. After uploading a file, they were not completely sure where to go to next. I have therefore redesigned the home page, adding large buttons (instead of the smaller text I had previously) with links to creating graphs and statistical tests.

I have also gone through many of the other pages in my application, such as analysis page, chisquare page, results page and the graph pages, redesigning the look. Although I was happy previously with the look, following the refactoring with bootstrap classes many of these pages no longer fit with the look of the rest of the website. Replacing many of the classes on these pages with bootstrap classes has helped my website look more cohesive as well as reducing the amount of custom CSS classes I have. In total, I have managed to drastically simplify my CSS code, reducing the file size considerably.

I have also refactored some of my HTML code, using more specific HTML tags instead of generic 'div' and 'span' tags everywhere.

I have also added to my D3.css file, allowing me to easily adjust font sizes on charts. Furthermore, I have added constants on the top of javascript files to define the colours used in the charts, so that it can easily be changed. The reason I did it here instead of the CSS file is because the mouse-over and mouse-out functions need to access this colour so it can change back to the original colour after the mouse moves out of the element. The function d3.select(this).style('fill') could also be used to select the current colour, however as there is a slight delay it means that very fast mouse movements over the elements will not select the right colour.

Tomorrow I will look at refactoring my python code (particularly on the graph routes page) before making my application public to get some final feedback.

<a name="latestEntry"></a>
### Finishing refactoring HTML and attempting to refactor python. (1st August)

I spent the morning continuing to refactor my HTML code. I added "titles" to all of my links, providing text as to where the link would take them. I also added alt text for all images and made the HTML tags more descriptive to provide semantic meaning. I hope that this will improve the accessibility of my application.

I have also added more questions to my feedback form, now totalling 10 questions. This will provide me with a more in depth review/feedback of my application now that it is coming to the final stages of development.

I have tried to refactor my python code. Whilst this was ok in some areas, I am still really struggling to refactor the analysis and graph routes. The analysis route is a very long function, with multiple 'if' statements that check and validate the type of test chosen with the selected variables. It does not seem it will be possible to factor these checks into a separate function, as any checks that fail need to return a re-render of the page along with a flash message. Likewise, the way the function is set up is quite different to the function used in "run_all_tests" (the automatic function that runs all statistical tests on a newly uploaded file). Although both involve statistical tests, they operate quite different (as on is in a route and needs flash statements and rendering HTML, whilst the other creates objects and adds to a database). I could likely spend a long time reviewing these functions without gaining a lot of ground and I feel at this point my time is better spent making a start on the dissertation write up. I will therefore put this on hold and maybe come back to it another day when I feel more comfortable with the progress of my write up.

##### Ongoing objectives

* Publish to public server and get final feedback.
* Start preparing for writing up dissertation.
* Increase file size allowance.
* To carry out unit testing graph saving and manual data input pages.
* Refactoring code.
