from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, ValidationError

from app.models import Subject


class SearchForm(FlaskForm):
    city = SelectField(coerce=int)
    subject = SelectField(coerce=int)
    submit = SubmitField('Search')

    def validate_subject(self, field):
        if not Subject.query.filter_by(id=field.data).first():
            raise ValidationError('non valid subject selected')


