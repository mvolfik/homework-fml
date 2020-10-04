from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user

from .db import User, db

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
        return redirect(url_for("homepage"))
    else:
        u.email_verification_token = None
        db.session.commit()
        flash("Email verified successfully, you can now log in")
        return redirect(url_for("homepage"))


# endregion
