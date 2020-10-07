import os

from flask import Flask, redirect, render_template, url_for
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect


def create_app():
    from . import sentry

    app = Flask(__name__)

    # region config

    app.config.from_mapping(
        {
            "SQLALCHEMY_DATABASE_URI": os.environ["DATABASE_URL"],
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "MONGODB_URI": os.environ["MONGODB_URI"],
            "MONGODB_DBNAME": os.environ["MONGODB_DBNAME"],
            "SECRET_KEY": os.environ["SECRET_KEY"],
            "REMEMBER_COOKIE_SECURE": True,
            "WTF_CSRF_TIME_LIMIT": 86400,  # 24 hours
        }
    )
    CSRFProtect(app)

    # endregion
    # region db

    from .db import init_app

    # BEWARE: it is important that this is run before importing any blueprints
    # that import mongo, mongodb, tasks
    init_app(app)

    # endregion
    # region utils

    from .utils import ErrorReason

    app.add_template_global(ErrorReason)

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

    @app.route("/favicon.ico")
    def favicon():
        return redirect(url_for("static", filename="favicon.ico"))

    # endregion

    return app
