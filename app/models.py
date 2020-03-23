from datetime import date

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from . import login_manager

#todo - if other fileds are added to these table
#todo - they must be promote to db.Model fore ease of handling
#many to many relationship junction_tables
tutor_subject = db.Table('tutor_subject',
                        db.Column('tutor_id', db.Integer, db.ForeignKey('tutors.id')),
                        db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id')))
#this_table_var = db.Table('this_table_name', db.Integer, db.ForeignKey('associated__tablename__.id'))
tutor_degree = db.Table('tutor_degree',
                        db.Column('tutor_id', db.Integer, db.ForeignKey('tutors.id')),
                        db.Column('degree_id', db.Integer, db.ForeignKey('degrees.id')))

class User(UserMixin, db.Model):
    #todo - eventually add other attributes
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    picture_filename = db.Column(db.String(150))
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    birth_date = db.Column(db.Date)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    about_me = db.Column(db.Text(), nullable=True)
    password_hash = db.Column(db.String(128))

    lessons_attended = db.relationship('Lesson', backref='User', lazy='dynamic')
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))

    type = db.Column(db.String(50))
    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':type
    }

    #it returns the lessons that have already been attended
    def get_stud_past_lessons_attended(self):
        lessons = []
        for l in self.lessons_attended:
            #todo - implement a better control to check whether a lesson is already attended within today
            if l.date <= date.today():
                lessons.append(l)
        return lessons
    #it returns the lessons booked but not yet attended
    def get_stud_pend_lessons_attended(self):
        lessons = []
        for l in self.lessons_attended:
            if l.date > date.today():
                lessons.append(l)
        return lessons


    def dontRemindMe(self):
        for l in self.get_stud_past_lessons_attended():
            l.dont_remind_me = True

    def __repr__(self):
        return 'username=' + self.username + ' - email=' + self.email + \
               '- password_hash=' + self.password_hash \
               +'- about_me=' + self.about_me

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

class Student(User):
    __tablename__ = 'students'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }


class Tutor(User):
    __tablename__ = 'tutors'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    degrees = db.relationship("Degree",secondary=tutor_degree)
    subjects = db.relationship('Subject', secondary=tutor_subject)

    lessons_tutored = db.relationship('Lesson', backref='Tutor', lazy='dynamic')

    #todo - implement the time slots through a built-in func/ad-hoc pkg
    #todo - make sure no more than 7 relationship are added
    #todo - make sure no double relationship
    day_av_slots = db.relationship('AvSlotsList', backref='Tutor', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': 'tutor',
    }

    #it returns the lessons already tutored
    def get_tutor_past_lessons(self):
        lessons=[]
        for l in self.lessons_tutored:
            # todo - implement a better control to check whether a lesson is already tutored within today
            if l.date <= date.today():
                lessons.append(l)
        return lessons

    # it returns the lessons booked that will be tutored
    def get_tutor_pend_lessons(self):
        lessons=[]
        for l in self.lessons_tutored:
            if l.date > date.today():
                lessons.append(l)
        return lessons

    #it returns a dictionary int:string --> 1:monday
    #it is useful to check if the tutor is available for certain week days
    def getAvDaysDict(self):
        dict = {}
        for d in self.day_av_slots:
            if d.week_day == 'monday':
                dict[1] = d.week_day
            if d.week_day == 'tuesday':
                dict[2] = d.week_day
            if d.week_day == 'wednesday':
                dict[3] = d.week_day
            if d.week_day == 'thursday':
                dict[4] = d.week_day
            if d.week_day == 'friday':
                dict[5] = d.week_day
            if d.week_day == 'saturday':
                dict[6] = d.week_day
            if d.week_day == 'sunday':
                dict[7] = d.week_day
        return dict

    #it returns a dictionary string:AvSlotsList --> monday:AvSlotsList
    #useful to check if the tutor is available during those time slots
    def getWeekDaySlotsDict(self):
        dict = {}
        for d in self.day_av_slots:
            if d.week_day == 'monday':
                dict[1] = d
            if d.week_day == 'tuesday':
                dict[2] = d
            if d.week_day == 'wednesday':
                dict[3] = d
            if d.week_day == 'thursday':
                dict[4] = d
            if d.week_day == 'friday':
                dict[5] = d
            if d.week_day == 'saturday':
                dict[6] = d
            if d.week_day == 'sunday':
                dict[7] = d
        return dict

    #it removes from the db all the notifications related to lessons tutored by this tutor
    #if the tutor has already seen those review there is no point to keep notifying him/her that
    def removeNotifications(self):
        for l in self.get_tutor_past_lessons():
            if l.notification is not None:
                db.session.delete(l.notification)


class Degree(db.Model):
    __tablename__ = 'degrees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return 'name=' + self.name +'- id=' + str(self.id)

    @staticmethod
    def insert_degrees():
        if Degree.query.first() is None:
            diploma = Degree(name='diploma')
            bachelor = Degree(name='bachelor')
            master = Degree(name='master')
            db.session.add_all([diploma, bachelor, master])
            db.session.commit()
            db.session.close()


class Subject(db.Model):#todo - eventually modify the kind of relationship
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    tutors = db.relationship("Tutor", secondary=tutor_subject)

    def __repr__(self):
        return 'name=' + self.name +'- id=' + str(self.id)

    @staticmethod
    def insert_subjects():
        if Subject.query.filter_by().first() is None:
            info_sys = Subject(name='information systems')
            accounting = Subject(name='accounting')
            economics = Subject(name='economics')
            db.session.add_all([info_sys, accounting, economics])
            db.session.commit()
            db.session.close()

class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(64))

    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    date = db.Column(db.Date)

    dont_remind_me = db.Column(db.Boolean)#set to true if the user does not want to keep seeing
                                          #the notification of the pending review

    review = db.relationship('Review', backref='Lesson', uselist=False)

    notification = db.relationship('Notification', backref='Lesson', uselist=False)
    #used to tell the tutor he/she got a review


class AvSlotsList(db.Model):
    __tablename__='av_day_slots'
    week_day = db.Column(db.String(30))
    id = db.Column(db.Integer, primary_key=True)

    slot1 = db.Column('07:00 - 08:00', db.Boolean())
    slot2 = db.Column('08:00 - 09:00', db.Boolean())
    slot3 = db.Column('09:00 - 10:00', db.Boolean())
    slot4 = db.Column('10:00 - 11:00', db.Boolean())
    slot5 = db.Column('11:00 - 12:00', db.Boolean())
    slot6 = db.Column('12:00 - 13:00', db.Boolean())
    slot7 = db.Column('13:00 - 14:00', db.Boolean())
    slot8 = db.Column('14:00 - 15:00', db.Boolean())
    slot9 = db.Column('15:00 - 16:00', db.Boolean())
    slot10 = db.Column('16:00 - 17:00', db.Boolean())
    slot11 = db.Column('17:00 - 18:00', db.Boolean())
    slot12 = db.Column('18:00 - 19:00', db.Boolean())

    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.id'))

    def __repr__(self):
        return 'week day=' + self.week_day + '- slot1=' + str(self.slot1) + '- slot2=' + str(self.slot2) \
               + '- slot3=' + str(self.slot3) + '- slot3=' + str(self.slot3) + '- slot4=' + str(self.slot4)\
               + '- slot5=' + str(self.slot5) + '- slot6=' + str(self.slot6) + '- slot7=' + str(self.slot7) \
               + '- slot8=' + str(self.slot8) +  '- slot9=' + str(self.slot9) + '- slot10=' + str(self.slot10) \
               + '- slot11=' + str(self.slot11) + '- slot12=' + str(self.slot12)

    #useful in the coding
    def getSlotsDict(self):
        dict = {}
        dict[1] = self.slot1
        dict[2] = self.slot2
        dict[3] = self.slot3
        dict[4] = self.slot4
        dict[5] = self.slot5
        dict[6] = self.slot6
        dict[7] = self.slot7
        dict[8] = self.slot8
        dict[9] = self.slot9
        dict[10] = self.slot10
        dict[11] = self.slot11
        dict[12] = self.slot12
        #print str(dict)
        return dict

class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text(), nullable=False)
    score = db.Column(db.Integer(), nullable=False)

    lesson_id = db.Column(db.Integer(), db.ForeignKey('lessons.id'), unique=True)


#it is only for tutor to notify them they got a review
class Notification(db.Model):
    __tablename__= 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True)

    lesson_id = db.Column(db.Integer(), db.ForeignKey('lessons.id'), unique=True)

class City(db.Model):#there is no need for a table with only a string attribute
     #but it could be useful having the users groupeb by city and for future developments
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship('User', backref='City', lazy='dynamic')

    @staticmethod
    def insert_cities():
         if City.query.first() is None:
             torino = City(name='TORINO')
             bologna = City(name='BOLOGNA')
             roma = City(name='ROMA')
             db.session.add_all([torino, bologna, roma])
             db.session.commit()
             db.session.close()