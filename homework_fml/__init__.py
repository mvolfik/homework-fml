import os

from flask import Flask, render_template


def create_app():
    app = Flask(__name__)

    # region config
    app.config.from_mapping(
        {
            "SQLALCHEMY_DATABASE_URI": os.environ["DATABASE_URL"],
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )
    # endregion

    # region db
    from .db import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)

    # endregion

    # region homepage
    @app.route("/")
    def homepage():
        return render_template("homepage.html")

    # endregion

    return app
