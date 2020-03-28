from flask import render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user

from app.main.views import checkForStudReviews, checkForTutReviews
from . import users_bp
from .forms import EditProfileForm, BookLessonForm, ReviewForm, BecomeTutor
from ..__init__ import db
from ..auth.forms import day_slots
from ..models import User, Subject, Tutor, Lesson, Review, Notification, City, Degree, Student
from app.myUtils import set_AvSlotsLists, setLessonTime


@users_bp.route('/user/<username>', methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter_by(username=str(username)).first()
    city = City.query.filter_by(id=user.city_id).first()
    if user is None:
        abort(404)
    return render_template('user/profile/profile.html', user=user, city=city)

@users_bp.route('/user/<name>/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile(name): #todo - make other attributes modificable
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        #current_user.city_id = form.city.data
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('users_bp.profile', username=current_user.username))

    #db_cities = City.query.order_by('name').all()
    #form.city.choices = [(g.id, g.name) for g in db_cities]
    city = City.query.filter_by(id=current_user.city_id).first()
    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template('user/profile/edit_profile.html', form=form, city=city)

@users_bp.route('/user/<username>/become_tutor', methods=['GET', 'POST'])
@login_required
def become_tutor(username):

    form = BecomeTutor()

    db_degrees = Degree.query.order_by('name').all()
    db_subjects = Subject.query.order_by('name').all()
    form.degrees.choices = [(g.id, g.name) for g in db_degrees]
    form.subjects.choices = [(g.id, g.name) for g in db_subjects]


    user = User.query.filter_by(username=str(username)).first()
    if user is None:
        abort(404)

    if form.validate_on_submit():
        if user.type == 'tutor':
            flash('you are already a tutor')
            return redirect(url_for('main.home'))

        user.type = 'tutor'


        new_tutor = Tutor(id=user.id, email=user.email, username=user.username, password=user.password,
                          about_me=user.about_me, name=user.name, surname=user.surname,
                          birth_date=user.birth_date, picture_filename=user.picture_filename, pay_rate=user.pay_rate)

        db.session.commit()



        # populate db.tutor object availability fields
        set_AvSlotsLists(form.mon_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.tue_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.wed_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.thu_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.fri_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.sat_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.sun_av_hours_slot, new_tutor)

        # populate db.tutor.degrees filed
        for d in form.degrees.data:
            degree = Degree.query.filter_by(id=d).first()
            new_tutor.degrees.append(degree)

        # populate db.tutor.subjects filed
        for s in form.subjects.data:
            subject = Subject.query.filter_by(id=s).first()
            subject.tutors.append(new_tutor)

        db.session.commit()

        flash('You are now registred as a tutor.')
        return redirect(url_for('main.home'))




    return render_template('/user/profile/become_tutor.html', user=user, form=form)


@users_bp.route('/user/<username>/book_lesson_with/<tutor_username>', methods=['GET', 'POST'])
@login_required
def book_lesson(username, tutor_username):
    form = BookLessonForm()

    tutor = Tutor.query.filter_by(username=tutor_username).first()#argument passed to render temaplate

    # some controls: the tutor_username argument passed is valid, the user is not booking with himself
    if tutor is None:
        flash('No user selected or the user you selected is not a tutor')
        return redirect(url_for('main.home'))
    elif str(tutor_username) == current_user.username:
        flash('you can not book a lesson with yourself')
        return redirect(url_for('main.home'))
    else:
        #populate form subject field
        db_subjects = tutor.subjects
        form.subject.choices = [(g.id, g.name) for g in db_subjects]


    if form.validate_on_submit():

        subject = Subject.query.filter_by(id=form.subject.data).first()

        print str(form.time.data) + '- type' + str(type(form.time.data))

        #form.subject is in tutor.subjects?
        if subject not in tutor.subjects:
            flash('This subject is not available for the selected tutor')
            return redirect(url_for('main.home'))
        elif not tutor.getWeekDaySlotsDict().has_key(form.day.data.isoweekday()):
            flash('the tutor is not available for that week day')
            return redirect(url_for('users_bp.book_lesson', username=current_user.username,
                                    tutor_username=tutor_username))
        else:
            for t in form.time.data:
                if tutor.getWeekDaySlotsDict().get(form.day.data.isoweekday()).getSlotsDict().get(int(t)) is not True:
                    flash('the tutor is not available for that/those time slots')
                    return redirect(url_for('users_bp.book_lesson', username=current_user.username,
                                            tutor_username=tutor_username))

            #insert stuff into db
            new_lesson = Lesson(subject_name=subject.name, date=form.day.data, time=setLessonTime(str(form.time.data)))

            current_user.lessons_attended.append(new_lesson)
            tutor.lessons_tutored.append(new_lesson)
            db.session.commit()


            flash('You booked the lesson!')
            return redirect(url_for('users_bp.lesson_payment', username=current_user.username))

    return render_template('user/lesson/book_lesson.html',tutor_username=tutor_username, form=form, tutor=tutor)

@users_bp.route('/user/<username>/pay_lesson', methods=['GET', 'POST'])
@login_required
def lesson_payment(username):
    us_id = User.query.filter_by(username=username).first().id
    lesson = Lesson.query.filter_by(user_id=us_id).first()
    tut_username = Tutor.query.filter_by(id=lesson.tutor_id).first().username
    price = Tutor.query.filter_by(id=lesson.tutor_id).first().pay_rate

    return render_template('/user/lesson/lesson_payment.html', username=username, lesson=lesson, tut_username=tut_username, price=price)



@users_bp.route('/user/<username>/stud_pend_lessons', methods=['GET', 'POST'])
@login_required
def stud_pend_lessons(username):
    lessons = User.query.filter_by(username=username).first().get_stud_pend_lessons_attended()

    dict ={}
    for l in lessons:
        dict[l.id] =Tutor.query.filter_by(id=l.tutor_id).first().username


    return render_template('/user/myLessons/stud_pend_lessons.html', lessons=lessons, dict=dict)

@users_bp.route('/user/<username>/stud_past_lessons', methods=['GET', 'POST'])
@login_required
def stud_past_lessons(username):
    lessons = User.query.filter_by(username=username).first().get_stud_past_lessons_attended()

    dict = {}
    for l in lessons:
        dict[l.id] = Tutor.query.filter_by(id=l.tutor_id).first().username


    return render_template('/user/myLessons/stud_past_lessons.html', lessons=lessons, dict= dict)

@users_bp.route('/user/<username>/tutor_pend_lessons', methods=['GET', 'POST'])
@login_required
def tutor_pend_lessons(username):
    lessons=[]
    dict = {}
    if Tutor.query.filter_by(username=username).first() is not None:
        lessons = Tutor.query.filter_by(username=username).first().get_tutor_pend_lessons()
        for l in lessons:
            dict[l.id] = User.query.filter_by(id=l.user_id).first().username
    return render_template('/user/myLessons/tutor_pend_lessons.html', lessons=lessons, dict=dict)

@users_bp.route('/user/<username>/tutor_past_lessons', methods=['GET', 'POST'])
@login_required
def tutor_past_lessons(username):

    lessons =[]
    dict = {}

    if Tutor.query.filter_by(username=username).first() is not None:
        lessons = Tutor.query.filter_by(username=username).first().get_tutor_past_lessons()
        for l in lessons:
            dict[l.id] = User.query.filter_by(id=l.user_id).first().username
    return render_template('/user/myLessons/tutor_past_lessons.html', lessons=lessons, dict=dict)

@users_bp.route('/user/<username>/review_lesson/<lesson_id>', methods=['GET', 'POST'])
@login_required
def review_lesson(username, lesson_id):
    form = ReviewForm()
    if form.validate_on_submit():
        #todo - implement controls

        score = 0
        if str(form.star.data) == '1-star':
            score = 1
        if str(form.star.data) == '2-stars':
            score = 2
        if str(form.star.data) == '3-stars':
            score = 3
        if str(form.star.data) == '4-stars':
            score = 4
        if str(form.star.data) == '5-stars':
            score = 5


        new_review = Review(comment=form.comment.data, score=score, lesson_id=lesson_id)
        db.session.add(new_review)
        new_notification = Notification(lesson_id=lesson_id)
        db.session.add(new_notification)
        db.session.commit()
        flash('The lesson has been reviewed')
        return redirect(url_for('main.home'))

    return render_template('/user/lesson/review_lesson.html', form=form, lesson_id=lesson_id)

@users_bp.route('/user/<username>/done_reviews', methods=['GET', 'POST'])
@login_required
def done_reviews(username):

    attended_lessons = User.query.filter_by(username=username).first().get_stud_past_lessons_attended()
    dict1 ={}
    dict2 = {}
    for l in attended_lessons:
        if l.review:
            dict1[l.id] = l.review
            dict2[l.id] = Tutor.query.filter_by(id=l.tutor_id).first().username


    return render_template('/user/reviews/done_reviews.html', lessons=attended_lessons, dict1=dict1, dict2=dict2)

@users_bp.route('/user/<username>/gotten_reviews', methods=['GET', 'POST'])
@login_required
def gotten_reviews(username):
    tut = Tutor.query.filter_by(username=username).first()
    print str(tut)
    tut_lessons = tut.get_tutor_past_lessons()
    dict1 = {}
    dict2 = {}
    print str(tut_lessons)
    for l in tut_lessons:
        print str(l.review)
        if l.review:
            dict1[l.id] = l.review
            dict2[l.id] = User.query.filter_by(id=l.user_id).first().username

    return render_template('/user/reviews/gotten_reviews.html', dict1 = dict1, dict2=dict2, lessons=tut_lessons)

