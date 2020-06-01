# Project Journal

This is a development journal that will be kept for the project duration and updated regularly with my progress.
It will contain information regarding what has been achieved recently and what will be looked at next.
Any specific problems I encounter or reflections that I may have will also be included.

- [Full installation list](documentation.md#installs)
- [Jump to the latest entry](#latestEntry)

<a name="latestEntry"></a>

### Pre-project setup (June 1st)

###### Goals

- Setup the preliminary folder structure, kanban board and project journal.
- Initialise a local project Git repository and remote repository on Github.
- Ensure all initial tools and programming languages required to get the project started are ready and installed, including [python3](https://www.python.org/downloads/) (and setting up a virtual environment), [Flask](https://flask.palletsprojects.com/en/1.1.x/installation/#installation), Javascript (specifically [D3.js](https://d3js.org/)) and [MongoDB](https://www.mongodb.com/). The full installation list will be kept up to date in the accompanying [code documentation](documentation.md#installs).

Following the initial installations above and after starting making a basic web application, it became apparent that I would need to handle web forms from the user (such as for file uploads).
For this I decided to download the flask extension [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/) which is a wrapper around the WTForms package.

```
pip3 install flask-wtf
```

I also installed a dropzone.js extension to allow fo easy uploading of files by dragging and dropping.

```
pip install Flask-Dropzone
```

After handling the file importing, I realised that one way to keep a record of that file is to save the file name in a database associated with that user. To do this, it would require having user accounts and subsequently a registration and login page. I therefore decided to implement these features at this point (and then at a later date I will return to handling 'guest' users, and how this information would be stored for these users without an account.)
