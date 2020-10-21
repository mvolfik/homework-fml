import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from citext import CIText
from flask_login import UserMixin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy(engine_options={"connect_args": {"options": "-c timezone=utc"}})
migrate = Migrate()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(CIText, unique=True, nullable=False)
    hash = db.Column(db.String, nullable=False)
    email_verification_token = db.Column(
        db.String, unique=True
    )  # simplest solution, once it's None, the user is verified

    services_data = db.Column(JSON)


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


@dataclass(init=False, eq=False)
class Task(db.Model):
    __tablename__ = "tasks"
    id: int = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User, backref="tasks")

    due: datetime = db.Column(db.DateTime, nullable=False)
    assigned_on: datetime = db.Column(db.DateTime, nullable=False)
    service_name: str = db.Column(db.String, nullable=False)
    full_text: str = db.Column(db.String, nullable=True)
    data: Any = db.Column(JSON)
