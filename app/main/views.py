from flask import render_template
from flask_login import current_user

from app import db
from app.main.forms import SearchForm
from app.myUtils import checkForStudReviews, checkForTutReviews
from . import main
from ..models import Degree, Subject, Tutor, City, User, Lesson
from datetime import date


@main.before_app_first_request
def populate_db():
    Degree.insert_degrees()
    Subject.insert_subjects()
    City.insert_cities()



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
    db_cities = City.query.order_by('name').all()
    sbj_None = Subject(name='', id=0)
    db_subjects.insert(0, sbj_None)
    city_None = City(name='', id=0)
    db_cities.insert(0, city_None)
    form.subject.choices = [(g.id, g.name) for g in db_subjects]
    form.city.choices = [(g.id, g.name) for g in db_cities]

    tutors = Tutor.query.all()#pass it as argument in render_template to show the list of tutors available for that
                              #selection

    if form.validate_on_submit():
        subject = Subject.query.filter_by(id=form.subject.data).first()
        selected_tutors = subject.tutors
        print str(subject.tutors)

        #render only the users for that city
        if City is not None:
            city = City.query.filter_by(id=form.city.data).first()
            if city is not None:
                for t in selected_tutors:
                    if not city.id == t.city_id:
                        selected_tutors.remove(t)

        return render_template('search.html', form=form, tutors=selected_tutors)

    return render_template('search.html',form=form, tutors=tutors,
                           unreviewed_stud_lessons = checkForStudReviews(current_user),
                           reviewed_lessons=checkForTutReviews(current_user))



