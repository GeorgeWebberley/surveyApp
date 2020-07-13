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
