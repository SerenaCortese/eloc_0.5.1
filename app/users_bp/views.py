from flask import render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user

from app.main.views import checkForStudReviews, checkForTutReviews
from . import users_bp
from .forms import EditProfileForm, BookLessonForm, ReviewForm
from ..__init__ import db
from ..auth.forms import day_slots
from ..models import User, Subject, Tutor, Lesson, Review, Notification


@users_bp.route('/user/<username>', methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter_by(username=str(username)).first()
    if user is None:
        abort(404)
    return render_template('user/profile/profile.html', user=user,
                           unreviewed_stud_lessons = checkForStudReviews(current_user),
                           reviewed_lessons=checkForTutReviews(current_user))

@users_bp.route('/user/<name>/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile(name): #todo - make other attributes modificable
    form = EditProfileForm()
    if form.validate_on_submit():
        #todo - make sure the user is modifying his/her own profile
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('users_bp.profile', username=current_user.username))
    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template('user/profile/edit_profile.html', form=form)


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
            new_lesson = Lesson(subject_name=subject.name, date=form.day.data)
            current_user.lessons_attended.append(new_lesson)
            tutor.lessons_tutored.append(new_lesson)
            db.session.commit()

            flash('You booked the lesson mate!')
            return redirect(url_for('users_bp.lesson_payment', username=current_user.username))

    return render_template('user/lesson/book_lesson.html',tutor_username=tutor_username, form=form, tutor=tutor)

@users_bp.route('/user/<username>/pay_lesson', methods=['GET', 'POST'])
@login_required
def lesson_payment(username):
    return render_template('/user/lesson/lesson_payment.html', username=username, day_slots=day_slots)



@users_bp.route('/user/<username>/stud_pend_lessons', methods=['GET', 'POST'])
@login_required
def stud_pend_lessons(username):
    lessons = User.query.filter_by(username=username).first().get_stud_pend_lessons_attended()
    return render_template('/user/myLessons/stud_pend_lessons.html', lessons=lessons)

@users_bp.route('/user/<username>/stud_past_lessons', methods=['GET', 'POST'])
@login_required
def stud_past_lessons(username):
    lessons = User.query.filter_by(username=username).first().get_stud_past_lessons_attended()
    User.query.filter_by(username=username).first().dontRemindMe()
    return render_template('/user/myLessons/stud_past_lessons.html', lessons=lessons)

@users_bp.route('/user/<username>/tutor_pend_lessons', methods=['GET', 'POST'])
@login_required
def tutor_pend_lessons(username):
    lessons=[]
    if Tutor.query.filter_by(username=username).first() is not None:
        lessons = Tutor.query.filter_by(username=username).first().get_tutor_pend_lessons()
    return render_template('/user/myLessons/tutor_pend_lessons.html', lessons=lessons)

@users_bp.route('/user/<username>/tutor_past_lessons', methods=['GET', 'POST'])
@login_required
def tutor_past_lessons(username):
    lessons =[]
    if Tutor.query.filter_by(username=username).first() is not None:
        lessons = Tutor.query.filter_by(username=username).first().get_tutor_past_lessons()
    return render_template('/user/myLessons/tutor_past_lessons.html', lessons=lessons)

@users_bp.route('/user/<username>/review_lesson', methods=['GET', 'POST'])
@login_required
def review_lesson(username, lesson):
    form = ReviewForm()
    if form.validate_on_submit():
        new_review = Review(comment=form.comment.data, score=form.score.data, lesson_id=lesson.id)
        db.session.add(new_review)
        new_notification = Notification(lesson_id=lesson.id)
        db.session.add(new_notification)
        db.session.commit()
        flash('The lesson has been reviewed')
        return redirect(url_for('main.home'))

    return render_template('/user/lesson/review_lesson.html')

@users_bp.route('/user/<username>/done_reviews', methods=['GET', 'POST'])
@login_required
def done_reviews(username):
    return render_template('/user/reviews/done_reviews.html')

@users_bp.route('/user/<username>/gotten_reviews', methods=['GET', 'POST'])
@login_required
def gotten_reviews(username):
    return render_template('/user/reviews/gotten_reviews.html')