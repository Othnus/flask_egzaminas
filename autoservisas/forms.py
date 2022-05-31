from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, PasswordField, IntegerField, SelectField, FloatField, DecimalField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email, Length, NumberRange

from autoservisas import models


MESSAGE_BAD_EMAIL = "Neteisingas El.paštas"

def car_query():
    return models.Car.query.filter_by(user_id=models.current_user.id)


class RegistrationForm(FlaskForm):
    login = StringField('Vardas', [DataRequired()])
    e_mail = StringField('El.paštas', [DataRequired(), Email(MESSAGE_BAD_EMAIL)])
    password = PasswordField('Slaptažodis', [DataRequired()])
    confirmation = PasswordField('Pakartokite slaptažodį', [EqualTo('password', "Slaptažodis nesutampa")])
    submit = SubmitField('Registruotis')


class LoginForm(FlaskForm):
    e_mail = StringField('El.paštas', [DataRequired(), Email(MESSAGE_BAD_EMAIL)])
    password = PasswordField('Slaptažodis', [DataRequired()])
    remember = BooleanField('Prisiminti mane')
    submit = SubmitField('Prisijungti')


class ProfileForm(FlaskForm):
    login = StringField('Vardas', [DataRequired()])
    e_mail = StringField('El.paštas', [DataRequired(), Email(MESSAGE_BAD_EMAIL)])
    submit = SubmitField('Atnaujinti')


class CarForm(FlaskForm):
    marke = StringField('Markė', [DataRequired()])
    model = StringField('Modelis', [DataRequired()])
    year = IntegerField('Pagaminimo metai', [DataRequired(), NumberRange(min=1908, max=2023, message='Neteisingai nurodyti pagaminimo metai')])
    engine = SelectField('Variklio tipas', [DataRequired()], choices=['benzinas', 'benzinas/dujos', 'benzinas/elektra', 'dyzelis', 'elektra'])
    registration = StringField('Valstybinis numeris', [DataRequired(), Length(min=1, max=6, message='Netinkamas simbolių skaičius')])
    vin = StringField('VIN', [DataRequired(), Length(min=11, max=17, message='Netinkamas simboliu skaičius')])
    submit = SubmitField('Išsaugoti')


class CreateFailureForm(FlaskForm):
    description = StringField('Gedimo aprašymas', [DataRequired()])
    car_id = QuerySelectField('Pasirinkite automobilį', query_factory=car_query, allow_blank=False, get_label=lambda obj: str(f'{obj.marke} {obj.model}, valstybinis: {obj.registration}'))
    submit = SubmitField('Išsaugoti')


class EditFailureForm(FlaskForm):
    status = SelectField('Būsena', choices=["naujas", "priimtas", "laukiame detalių", "remontuojamas",  "įvykdytas", "atiduotas"], default="naujas")
    price = DecimalField('Kaina', default=0)
    submit = SubmitField('Išsaugoti')
