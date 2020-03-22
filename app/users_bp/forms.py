from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, \
    SelectField, DateField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError

from app.auth.forms import day_slots


class EditProfileForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                              'Usernames must have only letters, numbers, dots or underscores')])
    about_me = TextAreaField()
    #todo - add the other fields
    submit = SubmitField('Edit')



class BookLessonForm(FlaskForm):
    subject = SelectField(coerce=int)
    day = DateField('day')
    time = SelectMultipleField('time', choices=day_slots)
    submit = SubmitField('Book')

    def validate_day(self, field):
        if field.data< date.today():
            raise ValidationError('it is not possible to book a lesson behind today')

class ReviewForm(FlaskForm):
    comment = TextAreaField('comment')
    score = IntegerField('score')
    submit = SubmitField('Review')