<a name="latestEntry"></a>
### Sprint 2 (starting 21st June)

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

### Review of sequence diagrams and database design (21st June)
The 'sequence' diagram from sprint 1 is still very much valid, with only some minor changes needed. Previously I carried out the data pre-processing on the server side and sent the reduced data set needed for creating graphs to the client. However, as described in [this](../sprint1/journal.md#dynamicGraph) section, giving the user the ability to choose their variables and axes on the graph page and get instant visualisation would likely reduce traffic of the user having to go back and forth with the server to get the result they want. Therefore I have updated the sequence diagram to show how the data processing for graphs occurs mostly on the client side in D3.js.


<p align="center">
  <img src="../diagrams/sequenceDiagram2.png" />
</p>

The design for the database has changed also since the preliminary design. In the original design, graphs and statistical tests referenced the 'survey' entity which in turn referenced the 'user' entity. This has since changed, with graphs, tests and surveys all referencing the 'user' entity, with graphs and tests also referencing the 'survey' entity. I have updated my diagram to reflect this.


<p align="center">
  <img src="../diagrams/databaseDesign2.png" />
</p>

As discussed previously, this design is flexible, meaning that the design of the 'graph' entity will vary considerable depending on the type of graph being made (e.g. different numbers of variables, x/y axes, aggregations etc.) Furthermore, I also expect the 'test' entity to vary depending on the type of test. This is an advantage of using a document based database such as MongoDB. The python code will be able to check the 'type' of graph/statistical test and then know how to read it accordingly.


### Bug fixing (21st June)

I explored the different possible reasons why the javascript file was not loading for one user when accessing the 'analyse' page for creating statistical tests. After some searching around on the internet, I realised that one possible reason could've been the use of an adblocker preventing some of the content being loaded. A lot of adblockers will identify any static files such as images, CSS and javascript files with 'suspicious' sounding names (names such as 'advert.jpg'). My javascript file for the analyse page was called 'analyse.js' which I thought could have been a culprit. I downloaded an adblocker extension to test it on my computer and discovered that changing the name from 'analyse.js' to 'statistic.js' solved the problem!

### Account edit (21st June)

One comment was to allow for editing account details. I have therefore added an 'account' page where users can update their email, first name or last name. I will update this soon to allow users to also reset their password.


##### Ongoing objectives

* Add more graphs. I think line graph would be a good next one to look at as it will be quite different to bar charts. Pie-charts I think will be quite similar to bar-charts as it is mostly categorical data and aggregations, only the presentation is different.
* Add more statistical tests.
* Add an export feature.
* Improve CSS to allow for responsive web pages (particularly on the bar chart page).
* Allow users to input survey data directly.
* To carry out unit testing of the bar-chart, statistics page and dashboard pages.
* Password reset.
