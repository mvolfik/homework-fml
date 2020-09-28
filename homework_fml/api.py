import secrets

from flask import Blueprint, flash, jsonify, render_template, request, url_for
from flask_login import LoginManager, login_user, logout_user
from passlib.context import CryptContext

from .db import User, db
from .email import send_mail
from .utils import ErrorReason

bp = Blueprint("api", __name__, url_prefix="/api")

# region setup

cryptctx = CryptContext(schemes=["argon2"])

login_manager = LoginManager()
login_manager.login_view = "user.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# endregion
# region errors


@bp.errorhandler(500)
def error(e):
    return jsonify({"ok": False, "reason": "EXCEPTION"})


@bp.errorhandler(400)
def bad_request(e):
    return jsonify({"ok": False, "reason": "EXCEPTION"})


# endregion


@bp.route("/register", methods=("POST",))
def register():
    data = request.form
    if len(data["pwd"]) < 8:
        return jsonify({"ok": False, "reason": ErrorReason.PASSWORD_TOO_SHORT})
    elif data["pwd"] != data["confirmpwd"]:
        return jsonify({"ok": False, "reason": ErrorReason.PASSWORDS_DIFFER})
    elif db.session.query(User.query.filter_by(email=data["email"]).exists()).scalar():
        return jsonify({"ok": False, "reason": ErrorReason.EMAIL_ALREADY_REGISTERED})
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
        return jsonify({"ok": False, "reason": ErrorReason.WRONG_LOGIN})
    elif u.email_verification_token is not None:
        return jsonify({"ok": False, "reason": ErrorReason.ACCOUNT_NOT_ACTIVE})

    valid, new_hash = cryptctx.verify_and_update(data["pwd"], u.hash)
    if not valid:
        return jsonify({"ok": False, "reason": ErrorReason.WRONG_LOGIN})

    else:
        login_user(u)
        if new_hash:
            u.hash = new_hash
            db.session.commit()
        return jsonify({"ok": True})


@bp.route("/resend-email", methods=("POST",))
def resend_email():
    u = User.query.filter_by(email=request.form["email"]).one_or_none()
    if u is None or u.email_verification_token is None:
        return jsonify({"ok": False, "reason": ErrorReason.EXCEPTION})
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


@bp.route("/logout", methods=("POST",))
def logout():
    logout_user()
    flash("You have been successfully logged out")
    return jsonify({"ok": True})
