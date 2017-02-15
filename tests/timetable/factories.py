import random

from faker import Faker

from app import db

from app.homework.models import Quiz, HomeworkType, Question, Essay
from tests.lessons.factories import LessonFactory
from app.timetable.models import Week, Period

fake = Faker()


class WeekFactory:
    def __init__(self, school):
        self.school = school

    def new(self):
        id = fake.random_int()

        week = Week(
            name=fake.first_name(),
            school_id=self.school.id
        )

        week.id = id

        return week

    def new_into_db(self, **kwargs):
        week = self.new()
        db.session.add(week)
        db.session.commit()
        return week


class PeriodFactory:
    def __init__(self, school):
        self.school = school

    def new(self, week_id=None):
        id = fake.random_int()

        if week_id is None:
            week = WeekFactory(school=self.school).new_into_db()
            week_id = week.id

        start_time = fake.time_object()
        end_time = fake.time_object()
        if start_time > end_time:
            placeholder = start_time
            start_time = end_time
            end_time = placeholder

        period = Period(
            week=week_id,
            day=random.randint(1, 5),
            start_time=start_time,
            end_time=end_time,
            name=fake.first_name()
        )

        period.id = id
        return period

    def new_into_db(self, **kwargs):
        period = self.new(**kwargs)
        db.session.add(period)
        db.session.commit()
        return period
