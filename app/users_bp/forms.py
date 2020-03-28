from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, \
    SelectField, DateField, SelectMultipleField, IntegerField, FloatField, RadioField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError

from app.auth.forms import day_slots


class EditProfileForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                              'Usernames must have only letters, numbers, dots or underscores')])
    about_me = TextAreaField()
    submit = SubmitField('Edit')



class BookLessonForm(FlaskForm):
    subject = SelectField(coerce=int)
    day = DateField('day')
    time = SelectField('time', choices=day_slots)
    submit = SubmitField('Book')

    def validate_day(self, field):
        if field.data< date.today():
            raise ValidationError('it is not possible to book a lesson behind today')

class ReviewForm(FlaskForm):
    comment = TextAreaField('comment')

    score = IntegerField('score')

    star = RadioField('rating', choices=[('5-stars', '&#9733;'), ('4-stars', '&#9733;'), ('3-stars', '&#9733;'), ('2-stars', '&#9733;'), ('1-star', '&#9733;')])


    submit = SubmitField('Review')


class BecomeTutor(FlaskForm):
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

    submit = SubmitField('Become Tutor')


    def validate_degrees(self, field):#todo - implement control
        pass

    def validate_subjects(self, field):#todo - implement control
        pass