import os
from app import app, dropzone
from flask import Flask, render_template, url_for, request, flash, redirect
from app.forms import RegistrationForm, LoginForm



@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    # Checks validation when form is submitted with submit button
    if form.validate_on_submit():
        flash("Account created successfully! You can now login!", "success")
        return redirect(url_for('index'))
    return render_template("register.html", title = 'Register', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template("login.html", title = 'Login', form = form)


@app.route('/import', methods=['GET', 'POST'])
def importFile():
    if request.method == "POST":
        f = request.files.get('file')
        f.save(os.path.join('app/uploads', f.filename))
    return render_template("import.html", title = "Import file")
