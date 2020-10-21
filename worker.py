import logging
import secrets

from flask import render_template, url_for

from homework_fml import create_app
from homework_fml.db import PasswordResetToken, User, db
from homework_fml.email import send_mail

app = create_app()
app.app_context().push()


def send_email_verification_mail(user_id):
    user = User.query.get(user_id)
    if user is None:
        logging.error("User is None when sending verification email")
        return False

    token_url = url_for(
        "user.verify_email", token=user.email_verification_token, _external=True,
    )
    send_mail(
        user.email,
        "Email verification",
        "Hello,\n"
        "Somebody (most likely you) just registered an account on homework-f.ml with this email address. In order to verify it, please open the following URL address in your browser:\n"
        + token_url
        + "\n"
        "In case it wasn't you, you don't need to take any action. The account is unusable without a verified email address.\n\n"
        "Best regards,\n"
        "Matěj from Homework – Fully Merged List",
        render_template(
            "mail/verify_email.html", title="Email verification", token=token_url,
        ),
    )


def create_and_send_password_reset_token(user_id):
    user = User.query.get(user_id)
    if user is None:
        logging.error("User is None when sending password reset email")
        return False

    token = secrets.token_hex(64)
    token_object = PasswordResetToken(token=token)
    user.password_reset_tokens.append(token_object)
    db.session.commit()

    token_url = url_for("user.reset_password", reset_token=token, _external=True)
    send_mail(
        user.email,
        "Password reset",
        "Hello,\n"
        "Somebody (most likely you) just requested password reset for account on homework-f.ml with this email address. If it was you, click the following link to set your new password:\n\n"
        + token_url
        + "\n\n"
        "In case it wasn't you, you don't need to take any action. Your password and account are safe.\n\n"
        "Best regards,\n"
        "Matěj from Homework – Fully Merged List",
        render_template(
            "mail/reset_password.html", title="Reset your password", token=token_url
        ),
    )
