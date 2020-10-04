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
