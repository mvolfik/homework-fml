import secrets
from datetime import datetime, timezone

from bson import ObjectId
from flask import Blueprint, flash, jsonify, render_template, request, url_for
from flask.json import JSONEncoder
from flask_login import LoginManager, current_user, login_user, logout_user
from passlib.context import CryptContext
from sqlalchemy.orm import joinedload

from .db import PasswordResetToken, User, db, tasks
from .email import send_mail
from .utils import ErrorReason

# region setup

bp = Blueprint("api", __name__, url_prefix="/api")
cryptctx = CryptContext(schemes=["argon2"])
login_manager = LoginManager()

# endregion
# region flask-login

login_manager.login_view = "user.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# endregion
# region json encoder


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime):
            return o.timestamp()
        else:
            return super().default(o)


bp.json_encoder = CustomJSONEncoder


# endregion
# region errors


def fail(r: ErrorReason):
    return jsonify({"ok": False, "reason": r})


@bp.errorhandler(500)
def error(e):
    return fail(ErrorReason.EXCEPTION)


@bp.errorhandler(400)
def bad_request(e):
    return fail(ErrorReason.EXCEPTION)


# endregion


@bp.route("/register", methods=("POST",))
def register():
    data = request.form
    if len(data["pwd"]) < 8:
        return fail(ErrorReason.PASSWORD_TOO_SHORT)
    elif data["pwd"] != data["confirmpwd"]:
        return fail(ErrorReason.PASSWORDS_DIFFER)
    elif db.session.query(User.query.filter_by(email=data["email"]).exists()).scalar():
        return fail(ErrorReason.EMAIL_ALREADY_REGISTERED)
    else:
        email_verification_token = secrets.token_hex(64)
        # noinspection PyArgumentList
        db.session.add(
            User(
                email=data["email"],
                hash=cryptctx.hash(data["pwd"]),
                email_verification_token=email_verification_token,
            )
        )
        db.session.commit()
        token_url = url_for(
            "user.verify_email", token=email_verification_token, _external=True
        )
        send_mail(
            data["email"],
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
        return jsonify({"ok": True})


@bp.route("/login", methods=("POST",))
def login():
    data = request.form
    u = User.query.filter_by(email=data["email"]).one_or_none()
    if u is None:
        return fail(ErrorReason.WRONG_LOGIN)

    valid, new_hash = cryptctx.verify_and_update(data["pwd"], u.hash)
    if not valid:
        return fail(ErrorReason.WRONG_LOGIN)

    if u.email_verification_token is not None:
        return fail(ErrorReason.ACCOUNT_NOT_ACTIVE)

    login_user(u)
    if new_hash:
        u.hash = new_hash
        db.session.commit()
    return jsonify({"ok": True})


@bp.route("/resend-email", methods=("POST",))
def resend_email():
    u = User.query.filter_by(email=request.form["email"]).one_or_none()
    if u is None or u.email_verification_token is None:
        return fail(ErrorReason.EXCEPTION)

    email_verification_token = secrets.token_hex(64)
    u.email_verification_token = email_verification_token
    db.session.commit()
    token_url = url_for(
        "user.verify_email", token=email_verification_token, _external=True
    )
    send_mail(
        u.email,
        "Email verification",
        "Hello,\n"
        "Somebody (most likely you) just registered an account on homework-f.ml with this email address. In order to verify it, please open the following URL address in your browser:\n\n"
        + token_url
        + "\n\n"
        "In case it wasn't you, you don't need to take any action. The account is unusable without a verified email address.\n\n"
        "Best regards,\n"
        "Matěj from Homework – Fully Merged List",
        render_template(
            "mail/verify_email.html", title="Email verification", token=token_url,
        ),
    )
    return jsonify({"ok": True})


@bp.route("/logout", methods=("POST",))
def logout():
    logout_user()
    flash("You have been successfully logged out")
    return jsonify({"ok": True})


@bp.route("/request-password-reset", methods=("POST",))
def request_password_reset():
    user = User.query.filter_by(email=request.form["email"]).one_or_none()
    if user is None:
        return jsonify({"ok": True})

    token = secrets.token_hex(64)
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
    token_object = PasswordResetToken(token=token)
    user.password_reset_tokens.append(token_object)
    db.session.commit()
    return jsonify({"ok": True})


@bp.route("/reset-password", methods=("POST",))
def reset_password():
    data = request.form
    token_object = PasswordResetToken.query.options(
        joinedload(PasswordResetToken.user)
    ).get(data["reset_token"])
    if token_object is None:
        return fail(ErrorReason.TOKEN_INVALID)
    if datetime.utcnow() > token_object.expires:
        return fail(ErrorReason.TOKEN_EXPIRED)

    if len(data["pwd"]) < 8:
        return fail(ErrorReason.PASSWORD_TOO_SHORT)
    if data["pwd"] != data["confirmpwd"]:
        return fail(ErrorReason.PASSWORDS_DIFFER)

    token_object.user.hash = cryptctx.hash(data["pwd"])
    db.session.delete(token_object)
    db.session.commit()

    return jsonify({"ok": True})


@bp.route("/add-manual-task", methods=("POST",))
def add_manual_task():
    data = request.form
    due = datetime.fromtimestamp(int(data["due_timestamp"]), tz=timezone.utc)
    if due <= datetime.now(tz=timezone.utc):
        return fail(ErrorReason.DUE_IN_PAST)

    tasks.insert_one(
        {
            "_provider": "manual",
            "user_id": current_user.id,
            "title": data["title"],
            "due": due,
            "description": data["description"],
        }
    )
    return jsonify({"ok": True})


@bp.route("/get-tasks", methods=("GET",))
def get_tasks():
    return jsonify(
        {"ok": True, "tasks": list(tasks.find({"user_id": current_user.id}))}
    )
