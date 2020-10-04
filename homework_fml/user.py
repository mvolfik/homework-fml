from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy.orm import joinedload

from .db import PasswordResetToken, User, db

bp = Blueprint("user", __name__, url_prefix="/user")


# region views


@bp.route("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("homepage"))
    return render_template("register.html")


@bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("homepage"))
    return render_template("login.html")


@bp.route("/verify-email/<token>")
def verify_email(token):
    u = User.query.filter_by(email_verification_token=token).one_or_none()
    if u is None:
        flash("Token expired, already used, or invalid")
        return redirect(url_for("user.login"))
    else:
        u.email_verification_token = None
        db.session.commit()
        flash("Email verified successfully, you can now log in")
        return redirect(url_for("user.login"))


@bp.route("/reset-password/<reset_token>")
def reset_password(reset_token):
    token_object = PasswordResetToken.query.options(
        joinedload(PasswordResetToken.user)
    ).get(reset_token)
    if token_object is None:
        flash("Password reset token already used, or invalid")
        return redirect(url_for("user.login"))
    elif datetime.utcnow() > token_object.expires:
        flash("Password reset token is expired")
        return redirect(url_for("user.login"))
    else:
        return render_template(
            "reset_password.html",
            user_email=token_object.user.email,
            reset_token=reset_token,
        )


# endregion
