from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, current_user

from autoservisas import db


class LimitedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    e_mail = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)
    is_worker = db.Column(db.Boolean(), default=False)

    def __repr__(self) -> str:
        return self.login


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marke = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    engine = db.Column(db.String(50), nullable=False)
    registration = db.Column(db.String(6), unique=True, nullable=False)
    vin = db.Column(db.String(17), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User")

    def __repr__(self) -> str:
        return f'{self.year} {self.marke} {self.model}; valstybinis nr: {self.registration}'


class Failure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), nullable=False)
    status = db.Column(db.String(50), default='naujas', nullable=False)
    price = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    car = db.relationship("Car", lazy=True)

    def __repr__(self) -> str:
        return self.description
