from flask import url_for
from surveyapp import mail
from flask_mail import Message



def send_email(user):
    token = user.get_reset_token()
    message = Message("Reset password request", sender="noreply@datasaur.com", recipients=[user.email])
    message.body = f"""You have requested a password reset for datasaur.dev\n
    Please follow the link to reset your password.\n
    {url_for("users.reset_password", token=token, _external=True)}
    \nIf you did not request this email then please ignore it!
    """
    mail.send(message)
