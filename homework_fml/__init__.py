import os
from importlib import import_module

from flask import Flask, flash, redirect, render_template, url_for
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect


def create_app():
    from . import sentry  # noqa

    app = Flask(__name__)

    # region config

    app.config.from_mapping(
        {
            "SQLALCHEMY_DATABASE_URI": os.environ["DATABASE_URL"],
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SECRET_KEY": os.environ["SECRET_KEY"],
            "REMEMBER_COOKIE_SECURE": True,
            "WTF_CSRF_TIME_LIMIT": 86400,  # 24 hours
            "SERVICES": [
                # list of available services, can be changed to loading from env, which allows turning modules on and off
                "manual",
            ],
        }
    )
    CSRFProtect(app)

    # endregion
    # region db

    from .db import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    # endregion
    # region utils

    from .utils import ErrorReason

    app.add_template_global(ErrorReason)

    # endregion
    # region services

    from .utils import service_modules

    # BEWARE: setup magic that needs to be run before other imports
    # (well, just modifying a dict, might not be an issue)
    for service_name in app.config["SERVICES"]:
        service_modules[service_name] = import_module(
            ".services." + service_name, package=__name__
        )

    for module in service_modules.values():
        if hasattr(module, "bp"):
            app.register_blueprint(module.bp)

    # endregion
    # region user

    from .user import bp as user_bp

    app.register_blueprint(user_bp)

    # endregion
    # region api

    from .api import bp as api_bp, login_manager

    app.register_blueprint(api_bp)
    login_manager.init_app(app)

    # endregion
    # region views

    @app.route("/")
    def homepage():
        return render_template(
            "main.html" if current_user.is_authenticated else "welcome.html"
        )

    @app.route("/service-menu")
    def service_menu():
        if not current_user.is_authenticated:
            flash("You need to login to view that page")
            return redirect(url_for("user.login"))

        return render_template("service_menu.html")

    @app.route("/favicon.ico")
    def favicon():
        return redirect(url_for("static", filename="favicon.ico"))

    # endregion

    return app
