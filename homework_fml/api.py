import secrets
from datetime import datetime

from flask import Blueprint, current_app, flash, jsonify, request
from flask.json import JSONEncoder
from flask_login import LoginManager, current_user, login_user, logout_user
from passlib.context import CryptContext
from sqlalchemy.orm import joinedload

from .db import PasswordResetToken, User, db
from .utils import ErrorReason, fail

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
        if isinstance(o, datetime):
            return o.timestamp()
        else:
            return super().default(o)


bp.json_encoder = CustomJSONEncoder


# endregion
# region errors


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
        u = User(
            email=data["email"],
            hash=cryptctx.hash(data["pwd"]),
            email_verification_token=secrets.token_hex(64),
        )
        db.session.add(u)
        db.session.commit()
        current_app.task_queue.enqueue("worker.send_email_verification_mail", u.id)
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
    user = User.query.filter_by(email=request.form["email"]).one_or_none()
    if user is None or user.email_verification_token is None:
        return fail(ErrorReason.EXCEPTION)

    email_verification_token = secrets.token_hex(64)
    user.email_verification_token = email_verification_token
    db.session.commit()
    current_app.task_queue.enqueue("worker.send_email_verification_mail", user.id)
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
    current_app.task_queue.enqueue(
        "worker.create_and_send_password_reset_token", user.id
    )
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


@bp.route("/get-tasks", methods=("GET",))
def get_tasks():
    if not current_user.is_authenticated:
        return fail(ErrorReason.UNAUTHORIZED)

    return jsonify({"ok": True, "tasks": current_user.tasks})
