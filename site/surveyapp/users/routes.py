from surveyapp import dropzone, mongo, bcrypt, mail
from flask import Flask, render_template, url_for, request, flash, redirect, Blueprint
# syntax for accessing files inside packages
from surveyapp.users.forms import (RegistrationForm, LoginForm,
UpdateAccountForm, RequestPasswordForm, PasswordResetForm)
from flask_login import current_user, login_user, logout_user, login_required
from surveyapp.models import User
from surveyapp.users.utils import send_email


users = Blueprint("users", __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    # Checks validation when form is submitted with submit button
    if form.validate_on_submit():
        # Decode with UTF-8 to make the hash a string rather than byte-code
        password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        # One user comment was to request the email validation to not be case sensitive. It is therefore saved in the database as lower case.
        mongo.db.users.insert_one({\
        "firstName" : form.first_name.data,\
        "lastName" : form.last_name.data,\
        "email" : form.email.data.lower(),\
        "password" : password_hash})
        flash("Account created successfully! You can now login.", "success")
        return redirect(url_for("users.login"))
    return render_template("users/register.html", title = "Register", form = form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data.lower()})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(email=user["email"], first_name=user["firstName"], last_name=user["lastName"], _id=user["_id"])
            # logs user into a session
            login_user(user_obj, remember=form.remember.data)
            # retrieve the page the user was attempting to access previously from the URL
            next_page = request.args.get("next")
            # and redirect them to that page (if it exists) using a ternary conditional
            flash("Logged in successfully.", "success")
            return redirect(next_page) if next_page else redirect(url_for("main.index"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("users/login.html", title = "Login", form = form)


@users.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('main.index'))


@users.route('/account', methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # Update the 'current_user' object
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        # Update the user in the database
        mongo.db.users.update_one({"_id": current_user._id},
        {"$set": {"firstName": form.first_name.data,\
                "lastName": form.last_name.data,\
                "email": form.email.data.lower()}})
        flash("Account details updated.", "success")
        return redirect(url_for('users.account'))
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.email.data = current_user.email
    return render_template("users/account.html", title = "Account", form = form)


@users.route('/reset_password', methods=["GET", "POST"])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RequestPasswordForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data.lower()})
        user_obj = User(email=user["email"], first_name=user["firstName"], last_name=user["lastName"], _id=user["_id"])
        send_email(user_obj)
        flash("An email has been sent with a password reset link", "success")
        return redirect(url_for("users.login"))
    return render_template("users/request_reset.html", title="Password Reset", form=form)


@users.route('/reset_password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    user = User.verify_reset_token(token)
    if not user:
        flash("That token is invalid or has expired", "warning")
        return redirect(url_for("request_reset"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Decode with UTF-8 to make the hash a string rather than byte-code
        password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        # One user comment was to request the email validation to not be case sensitive. It is therefore saved in the database as lower case.
        mongo.db.users.update_one({"_id": user["_id"]},
        {"$set": {"password": password_hash}})
        flash("Password updated! You can now login.", "success")
        return redirect(url_for("users.login"))
    return render_template("users/reset_password.html", title="Password Reset", form=form)
