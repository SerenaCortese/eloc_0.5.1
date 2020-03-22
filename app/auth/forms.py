from datetime import date

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, \
    SubmitField, SelectMultipleField, TextAreaField, FloatField, DateField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo

from app import images
from ..models import User
from ..myUtils import day_slots


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('The email is not registered')

    def validate_password(self, field):
        if User.query.filter_by(email=self.email.data).first():
            if not User.query.filter_by(email=self.email.data).first().verify_password(field.data):
                raise ValidationError('password incorrect')

class StudRegFrom(FlaskForm):
    profile_picture = FileField(validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username',validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                              'Usernames must have only letters, numbers, dots or underscores')])
    name = StringField('name', validators=[DataRequired(), Length(1,64)])#todo - add regex
    surname = StringField('surname', validators=[DataRequired(), Length(1,64)])#todo - add regex
    birth_date = DateField('birth date')
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    about_me = TextAreaField()
    submit = SubmitField('Register')

    def validate_email(self, field):
     if User.query.filter_by(email=field.data).first():
         raise ValidationError('Email already in use')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')

    def validate_birth_date(self, field):#todo - add further controls
        if field.data>date.today():
            raise ValidationError('you can not be born in the future')

class TutorRegForm(StudRegFrom):
    degrees = SelectMultipleField(coerce=int)#degrees is a list of db.degree.id
    subjects = SelectMultipleField(coerce=int)#subjects is a list of db.Subject.id
    pay_rate = FloatField()

    #todo - implement controls on the fields below
    mon_av_hours_slot = SelectMultipleField('monday', choices=day_slots)
    tue_av_hours_slot = SelectMultipleField('tuesday', choices=day_slots)
    wed_av_hours_slot = SelectMultipleField('wednesday', choices=day_slots)
    thu_av_hours_slot = SelectMultipleField('thursday', choices=day_slots)
    fri_av_hours_slot = SelectMultipleField('friday', choices=day_slots)
    sat_av_hours_slot = SelectMultipleField('saturday', choices=day_slots)
    sun_av_hours_slot = SelectMultipleField('sunday', choices=day_slots)


    def validate_degrees(self, field):#todo - implement control
        pass

    def validate_subjects(self, field):#todo - implement control
        pass




