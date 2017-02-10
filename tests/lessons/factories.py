from faker import Faker

from app import db

from app.lessons.models import Subject, Lesson

fake = Faker()


class SubjectFactory:

    def __init__(self, school):
        self.school = school

    def new(self):
        id = fake.random_int()
        subject = Subject(
            name=fake.first_name(),
            school_id=self.school.id
        )
        subject.id = id
        return subject

    def new_into_db(self, **kwargs):
        subject = self.new()
        db.session.add(subject)

        db.session.commit()
        return subject


class LessonFactory:
    def __init__(self, school):
        self.school = school

    def new(self, subject=None, teachers=[], students=[]):
        if subject is None:
            subject = SubjectFactory(self.school).new_into_db()

        id = fake.random_int()
        lesson = Lesson(
            name=fake.first_name(),
            school_id=self.school.id,
            subject_id=subject.id
        )
        while Lesson.query.filter_by(name=lesson.name, school_id=self.school.id).first() is not None:
            lesson.name = fake.first_name()

        for teacher in teachers:
            lesson.teachers.append(teacher)

        for student in students:
            lesson.students.append(student)

        lesson.id = id
        return lesson

    def new_into_db(self, **kwargs):
        lesson = self.new(**kwargs)
        db.session.add(lesson)
        db.session.commit()
        return lesson
