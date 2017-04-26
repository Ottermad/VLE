import datetime

from faker import Faker

from app import db

from app.homework.models import Quiz, HomeworkType, Question, Essay, QuizAnswer, QuizSubmission, EssaySubmission, \
    Comment
from tests.lessons.factories import LessonFactory
from tests.user.factories import UserFactory

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


class QuizSubmissionFactory:
    def __init__(self, school):
        self.school = school

    def new(self, quiz=None, user_id=None):
        if user_id is None:
            user = UserFactory(school=self.school).new_into_db(permissions=['Student'])
            user_id = user.id

        if quiz is None:
            quiz = QuizFactory(school=self.school).new_into_db()

        submission = QuizSubmission(
            homework_id=quiz.id,
            user_id=user_id,
            datetime_submitted=datetime.datetime.now()
        )

        submission.id = fake.random_int()

        for question in quiz.questions:
            answer = QuizAnswer(fake.first_name(), submission.id, question.id)
            submission.answers.append(answer)
        return submission

    def new_into_db(self, **kwargs):
        quiz_submission = self.new(**kwargs)
        db.session.add(quiz_submission)
        db.session.commit()
        return quiz_submission


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


class EssaySubmissionFactory:
    def __init__(self, school):
        self.school = school

    def new(self, essay=None, user_id=None):
        if essay is None:
            essay = EssayFactory(school=self.school).new_into_db()

        if user_id is None:
            user = UserFactory(school=self.school).new_into_db(permissions=['Student'])
            user_id = user.id

        submission = EssaySubmission(
            homework_id=essay.id,
            user_id=user_id,
            datetime_submitted=datetime.datetime.now(),
            text=fake.first_name()
        )

        submission.id = fake.random_int()

        return submission

    def new_into_db(self, **kwargs):
        essay_submission = self.new(**kwargs)
        db.session.add(essay_submission)
        db.session.commit()
        return essay_submission


class CommentFactory:
    def __init__(self, school):
        self.school = school

    def new(self, submission_id=None, user_id=None):
        if submission_id is None:
            submission = EssaySubmissionFactory(school=self.school).new_into_db()
            submission_id = submission.id

        if user_id is None:
            user = UserFactory(school=self.school).new_into_db(permissions=['Teacher'])
            user_id = user.id

        comment = Comment(
            text=fake.first_name(),
            user_id=user_id,
            submission_id=submission_id
        )

        comment.id = fake.random_int()
        return comment

    def new_into_db(self, **kwargs):
        comment = self.new(**kwargs)
        db.session.add(comment)
        db.session.commit()
        return comment
