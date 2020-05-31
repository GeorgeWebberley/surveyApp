import os
from app import app, dropzone
from flask import Flask, render_template, request



@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/import', methods=['GET', 'POST'])
def importFile():
    if request.method == "POST":
        f = request.files.get('file')
        f.save(os.path.join('app/uploads', f.filename))
    return render_template("import.html", title = "Import file")
