import os
from importlib import import_module

import rq
from flask import Flask, flash, redirect, render_template, url_for
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect
from redis import Redis


def create_app():
    from . import sentry  # noqa

    app = Flask(__name__)

    # region config

    app.config.from_mapping(
        {
            "PREFERRED_URL_SCHEME": "https",
            "REDIS_URL": os.environ["REDIS_URL"],
            "REDIS_QUEUE_NAME": os.environ["REDIS_QUEUE_NAME"],
            "SECRET_KEY": os.environ["SECRET_KEY"],
            "SERVER_NAME": os.environ.get("SERVER_NAME", "homework-f.ml"),
            "SQLALCHEMY_DATABASE_URI": os.environ["DATABASE_URL"],
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
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
    # region redis

    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.task_queue = rq.Queue(app.config["REDIS_QUEUE_NAME"], connection=app.redis)

    # endregion
    # region utils

    from .utils import ErrorReason

    app.add_template_global(ErrorReason)

    # endregion
    # region services

    app.service_modules = {}

    for service_name in app.config["SERVICES"]:
        app.service_modules[service_name] = import_module(
            ".services." + service_name, package=__name__
        )

    for module in app.service_modules.values():
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
