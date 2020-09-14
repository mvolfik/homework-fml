import os

from flask import Flask


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

    return app
