import secrets
from datetime import datetime, timedelta

from citext import CIText
from flask_login import UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


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
        default=lambda: datetime.utcnow() + timedelta(hours=12),
    )
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User, backref="password_reset_tokens")
