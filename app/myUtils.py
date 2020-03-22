
####### AUTH #######
# todo - replace this shit with something cleaver
from datetime import date

from app import db
from app.models import AvSlotsList, User, Tutor

day_slots = [('1', '07:00 - 08:00'),
             ('2', '08:00 - 09:00'),
             ('3', '09:00 - 10:00'),
             ('4', '10:00 - 11:00'),
             ('5', '11:00 - 12:00'),
             ('6', '12:00 - 13:00'),
             ('7', '13:00 - 14:00'),
             ('8', '14:00 - 15:00'),
             ('9', '15:00 - 16:00'),
             ('10', '16:00 - 17:00'),
             ('11', '17:00 - 18:00'),
             ('12','18:00 - 19:00')]

def set_AvSlotsLists(formDaySlots, new_tutor):
    if formDaySlots.data:
        new_AvSlotsList = AvSlotsList(week_day=str(formDaySlots.label.text))
        for slot in formDaySlots.data:
            if slot == '1':
                new_AvSlotsList.slot1 = True
            if slot == '2':
                new_AvSlotsList.slot2 = True
            if slot == '3':
                new_AvSlotsList.slot3 = True
            if slot == '4':
                new_AvSlotsList.slot4 = True
            if slot == '6':
                new_AvSlotsList.slot6 = True
            if slot == '7':
                new_AvSlotsList.slot7 = True
            if slot == '8':
                new_AvSlotsList.slot8 = True
            if slot == '8':
                new_AvSlotsList.slot8 = True
            if slot == '9':
                new_AvSlotsList.slot9 = True
            if slot == '10':
                new_AvSlotsList.slot10 = True
            if slot == '11':
                new_AvSlotsList.slot11 = True
            if slot == '12':
                new_AvSlotsList.slot12 = True
        if new_tutor is not None:
            new_tutor.day_av_slots.append(new_AvSlotsList)

############################


####### notifications implementation #######

def checkForStudReviews(current_user):
    unreviewed_lessons = []
    if current_user.is_authenticated:
        for l in User.query.filter_by(username=current_user.username).first().lessons_attended:
            if l.review is None and l.dont_remind_me is not True \
                    and l.date < date.today():
                unreviewed_lessons.append(l)
    return unreviewed_lessons

def checkForTutReviews(current_user):
    reviewed_lessons = []
    if current_user.is_authenticated:
        if User.query.filter_by(username=current_user.username).first().type == 'tutor':
            for l in Tutor.query.filter_by(username=current_user.username).first().lessons_tutored:
                if l.review is not None and l.notification is not None \
                        and l.date < date.today():
                    reviewed_lessons.append(l)

    return reviewed_lessons

############################
