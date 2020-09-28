import os

from flask import Flask, render_template
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
            "SECRET_KEY": os.environ["SECRET_KEY"],
            "REMEMBER_COOKIE_SECURE": True,
            "WTF_CSRF_TIME_LIMIT": 86400,  # 24 hours
        }
    )
    CSRFProtect(app)

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
    # region db

    from .db import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    # endregion
    # region homepage

    @app.route("/")
    def homepage():
        return render_template(
            "main.html" if current_user.is_authenticated else "welcome.html"
        )

    # endregion

    return app
