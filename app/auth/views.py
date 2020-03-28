import os

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.utils import secure_filename

from . import auth
from .forms import LoginForm, StudRegFrom, TutorRegForm
from ..__init__ import db  # todo - check if it is the right istance of db
from ..models import User, Student, Subject, Degree, Tutor, City
from ..myUtils import set_AvSlotsLists


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user, form.remember_me.data)
        flash('You logged in.')
        return redirect(request.args.get('next') or url_for('main.home'))

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.home'))


@auth.route('/registration/reg')
def reg():
    return render_template('auth/registration/reg.html')

@auth.route('/registration/stud_reg', methods=['GET', 'POST'])
def stud_reg():
    form = StudRegFrom()

    #populate form filed
    db_cities = City.query.order_by('name').all()
    form.city.choices = [(g.id, g.name) for g in db_cities]

    if form.validate_on_submit():
        f = form.profile_picture.data
        filename = secure_filename(f.filename)
        path = os.path.dirname(os.path.dirname(__file__))
        join_path = os.path.join(path,'static', 'photos')
        f.save(os.path.join(join_path, filename))
        new_student = Student(email=form.email.data, username=form.username.data, password=form.password.data,
                              about_me=form.about_me.data, name=form.name.data, surname=form.surname.data,
                              birth_date=form.birth_date.data, picture_filename=filename)

        city = City.query.filter_by(id=form.city.data).first()
        new_student.city_id = city.id

        db.session.add(new_student)
        db.session.commit()
        flash('You have succesfully registred as a student.')
        return redirect(url_for('main.home'))

    return render_template('auth/registration/stud_reg.html', form=form)

@auth.route('/registration/tutor_reg', methods=['GET', 'POST'])
def tutor_reg():
    form = TutorRegForm()

    #bugs
    #todo - fix error - on the second registration - the user it is logged on the registration
    #todo - for some reason it happens only on the second registration

    #populate form fileds
    db_degrees = Degree.query.order_by('name').all()
    db_subjects = Subject.query.order_by('name').all()
    db_cities = City.query.order_by('name').all()
    form.degrees.choices = [(g.id, g.name) for g in db_degrees]
    form.subjects.choices = [(g.id, g.name) for g in db_subjects]
    form.city.choices = [(g.id, g.name) for g in db_cities]

    if form.validate_on_submit():
        f = form.profile_picture.data
        filename = secure_filename(f.filename)
        path = os.path.dirname(os.path.dirname(__file__))
        join_path = os.path.join(path,'static', 'photos')
        f.save(os.path.join(join_path, filename))

        new_tutor = Tutor(email=form.email.data, username=form.username.data,password=form.password.data,
                              about_me=form.about_me.data, name=form.name.data, surname=form.surname.data,
                              birth_date=form.birth_date.data, picture_filename=filename ,pay_rate=form.pay_rate.data)

        #populate db.tutor object availability fields
        set_AvSlotsLists(form.mon_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.tue_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.wed_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.thu_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.fri_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.sat_av_hours_slot, new_tutor)
        set_AvSlotsLists(form.sun_av_hours_slot, new_tutor)

        #populate db.tutor.degrees filed
        for d in form.degrees.data:
            degree = Degree.query.filter_by(id=d).first()
            new_tutor.degrees.append(degree)

        #populate db.tutor.subjects filed
        for s in form.subjects.data:
            subject = Subject.query.filter_by(id=s).first()
            subject.tutors.append(new_tutor)

        city = City.query.filter_by(id=form.city.data).first()
        new_tutor.city_id = city.id

        db.session.commit()

        flash('You have succesfully registred as a tutor.')
        return redirect(url_for('main.home'))

    return render_template('auth/registration/tutor_reg.html', form=form)