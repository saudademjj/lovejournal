from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from . import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_login_at = db.Column(db.DateTime)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class Entry(db.Model):
    __tablename__ = "entry"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    content = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255))
    tags = db.Column(db.String(255))


class KeyDate(db.Model):
    __tablename__ = "key_date"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False, index=True)
    location = db.Column(db.String(255))
    tags = db.Column(db.String(255))


class Photo(db.Model):
    __tablename__ = "photo"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
    caption = db.Column(db.String(255))
    location = db.Column(db.String(255))
    tags = db.Column(db.String(255))
