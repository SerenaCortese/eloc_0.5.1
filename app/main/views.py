from flask import render_template
from flask_login import current_user

from app import db
from app.main.forms import SearchForm
from app.myUtils import checkForStudReviews, checkForTutReviews
from . import main
from ..models import Degree, Subject, Tutor


@main.before_app_first_request
def populate_db():
    Degree.insert_degrees()
    Subject.insert_subjects()



@main.route('/home', methods=['GET', 'POST'])
@main.route('/', methods=['GET', 'POST'])
def home(): #todo - moidfy the func scope
    tutors = Tutor.query.all()

    return render_template('index.html', tutors=tutors,
                           unreviewed_stud_lessons = checkForStudReviews(current_user),
                           reviewed_lessons=checkForTutReviews(current_user))


@main.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()

    #popualte form
    db_subjects = Subject.query.order_by('name').all()
    sbj_None = Subject(name='', id=0)
    db_subjects.insert(0, sbj_None)
    form.subject.choices = [(g.id, g.name) for g in db_subjects]

    tutors = Tutor.query.all()#pass it as argument in render_template to show the list of tutors available for that
                              #selection

    if form.validate_on_submit():
        subject = Subject.query.filter_by(id=form.subject.data).first()
        return render_template('search.html', form=form, tutors=subject.tutors)

    return render_template('search.html',form=form, tutors=tutors,
                           unreviewed_stud_lessons = checkForStudReviews(current_user),
                           reviewed_lessons=checkForTutReviews(current_user))



