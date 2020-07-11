from flask import url_for
from surveyapp import mail
from flask_mail import Message



def send_email(user):
    print(user)
    print(user.email)
    token = user.get_reset_token()
    message = Message("Reset password request", sender="noreply@datasaur.com", recipients=[user.email])
    message.body = f"""you have requested a password reset for surveysite.com
    {url_for("users.reset_password", token=token, _external=True)}
    If you did not request this email then please ignore it!
    """
    mail.send(message)
