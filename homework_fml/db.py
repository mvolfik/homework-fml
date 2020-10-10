import secrets
from datetime import datetime, timedelta, timezone

from bson import CodecOptions
from citext import CIText
from flask_login import UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

db = SQLAlchemy(engine_options={"connect_args": {"options": "-c timezone=utc"}})
migrate = Migrate()

mongo: MongoClient = None
mongodb: Database = None
tasks: Collection = None


def init_app(app):
    global db, migrate, mongo, mongodb, tasks

    db.init_app(app)
    migrate.init_app(app, db)

    mongo = MongoClient(app.config["MONGODB_URI"])
    mongodb = mongo[app.config["MONGODB_DBNAME"]]
    tasks = mongodb.get_collection(
        "tasks", codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc)
    )


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(CIText, unique=True, nullable=False)
    hash = db.Column(db.String, nullable=False)
    email_verification_token = db.Column(
        db.String, unique=True
    )  # simplest solution, once it's None, the user is verified


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    token = db.Column(
        db.String(128), primary_key=True, default=lambda: secrets.token_hex(64)
    )
    expires = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(tz=timezone.utc) + timedelta(hours=12),
    )
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User, backref="password_reset_tokens")
