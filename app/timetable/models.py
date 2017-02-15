from enum import Enum
from datetime import time
from app import db
from app.lessons.models import Lesson


class Week(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))

    def __init__(self, name, school_id):
        self.name = name
        self.school_id = school_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'school_id': self.school_id
        }


class Day(Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5


class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('week.id'))
    day = db.Column(db.Integer)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    name = db.Column(db.String(120))

    week = db.relationship('Week', backref=db.backref('week', lazy='dynamic'))

    def __init__(self, week, day, start_time, end_time, name):
        self.week = week
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.name = name

    def to_dict(self, nest_week=False):
        period_dict = {
            'week_id': self.week_id,
            'day': self.day,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'name': self.name
        }
        if nest_week:
            period_dict['week'] = self.week.to_dict()
        return period_dict


class TimetabledLesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey('period.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))

    period = db.relationship('Period', backref=db.backref('period', lazy='dynamic'))
    lesson = db.relationship('Lesson', backref=db.backref('lesson', lazy='dynamic'))

    def __init__(self, period_id, lesson_id):
        self.period_id = period_id
        self.lesson_id = lesson_id

    def to_dict(self):
        return {
            'period': self.period.to_dict(nest_week=True),
            'lesson': self.lesson.to_dict()
        }

"""
for lesson in user.lessons_attending:
    periods = lesson.timetabled_lessons
"""