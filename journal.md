# Project Journal

This is a development journal that will be kept for the project duration and updated regularly with my progress.
It will contain information regarding what has been achieved recently and what will be looked at next.
Any specific problems I encounter or reflections that I may have will also be included.

- [Full installation list](#installs)
- [Jump to the latest entry](#latestEntry)

<a name="latestEntry"></a>

### Pre-project setup (June 1st)

###### Goals

- Setup the preliminary folder structure, kanban board and project journal.
- Initialise a local project Git repository and remote repository on Github.
- Ensure all initial tools and programming languages required to get the project started are ready and installed, including [python3](https://www.python.org/downloads/) (and setting up a virtual environment), [Flask](https://flask.palletsprojects.com/en/1.1.x/installation/#installation), Javascript (specifically [D3.js](https://d3js.org/)) and [MongoDB](https://www.mongodb.com/). The full installation list will be kept up to date in the accompanying [code documentation](documentation.md#installs).

Following the initial installations above and after starting making a basic web application, it became apparent that I would need to handle web forms from the user (for user input and file uploads).
For this I decided to download the flask extension Flask-WTF which is a wrapper around the WTForms package.

```
pip3 install flask-wtf
```

<a name="installs"></a>

### Full installation list

Requires having homebrew already installed.

python 3

```
brew install python
```

MongoDB
