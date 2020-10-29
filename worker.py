import logging
import secrets
from functools import wraps

from flask import current_app, render_template, url_for
from sentry_sdk import set_user
from sqlalchemy.orm import joinedload

from homework_fml.db import PasswordResetToken, Task, User, db
from homework_fml.email import send_mail


def job_with_user_id(f):
    @wraps(f)
    def wrapper(*args, user_id, **kwargs):
        u = User.query.get(user_id)
        set_user({"email": u.email, "id": u.id})
        f(*args, user_id=user_id, **kwargs)

    return wrapper


@job_with_user_id
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


@job_with_user_id
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


@job_with_user_id
def import_all(user_id):
    user = User.query.options(joinedload(User.tasks)).get(user_id)
    if user is None:
        logging.error("Trying to import tasks for nonexistent user_id")

    tasks = []
    for service_name, service in current_app.service_modules.items():
        for task in service.import_data(user):
            task_dict = {
                col.name: getattr(task, col.name)
                for col in Task.__table__.columns
                if getattr(task, col.name) is not None
            }
            task_dict["service_name"] = service_name
            task_dict["user_id"] = user_id
            tasks.append(task_dict)
    if tasks:
        query = Task.__table__.insert().values(tasks).returning(Task.id)
        results = db.session.execute(query)
        task_ids = [result[0] for result in results.fetchall()]
    else:
        task_ids = []

    db.session.commit()  # in case services store some data (e.g. new refresh token)
    return task_ids
