from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10000))
    length = db.Column(db.Float)
    is_minutes = db.Column(db.Boolean, default=True)
    url = db.Column(db.String(10000))
    date = db.Column(db.Date, default=func.current_date())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    workouts = db.relationship('Workout')