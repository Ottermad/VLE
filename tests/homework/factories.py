import random

from faker import Faker

from app import db

from app.homework.models import Quiz, HomeworkType, Question, Essay
from tests.lessons.factories import LessonFactory

fake = Faker()


class QuestionFactory:
    @classmethod
    def new(cls, quiz_id):
        question = Question(
            homework_id=quiz_id,
            question_text=fake.first_name(),
            question_answer=fake.first_name()
        )
        return question


class QuizFactory:
    def __init__(self, school):
        self.school = school

    def new(self, lesson_id=None):
        id = fake.random_int()

        if lesson_id is None:
            lesson = LessonFactory(school=self.school).new_into_db()
            lesson_id = lesson.id

        type_id = HomeworkType.HOMEWORK.value
        date_due = fake.date_time_this_year(after_now=True).date

        quiz = Quiz(
            lesson_id=lesson_id,
            title=fake.first_name(),
            description=fake.first_name(),
            date_due=date_due(),
            number_of_questions=fake.random_int()
        )

        quiz.id = id

        for n in range(0, quiz.number_of_questions):
            question = QuestionFactory.new(quiz.id)
            quiz.questions.append(question)

        return quiz

    def new_into_db(self, **kwargs):
        quiz = self.new(**kwargs)
        db.session.add(quiz)
        db.session.commit()
        return quiz


class EssayFactory:
    def __init__(self, school):
        self.school = school

    def new(self, lesson_id=None):
        id = fake.random_int()

        if lesson_id is None:
            lesson = LessonFactory(school=self.school).new_into_db()
            lesson_id = lesson.id

        type_id = HomeworkType.ESSAY.value
        date_due = fake.date_time_this_year(after_now=True).date

        essay = Essay(
            lesson_id=lesson_id,
            title=fake.first_name(),
            description=fake.first_name(),
            date_due=date_due(),
        )

        essay.id = id
        return essay

    def new_into_db(self, **kwargs):
        essay = self.new(**kwargs)
        db.session.add(essay)
        db.session.commit()
        return essay
