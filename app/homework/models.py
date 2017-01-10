import datetime
from enum import Enum

from app import db


class HomeworkType(Enum):
    HOMEWORK = 0
    ESSAY = 1
    QUIZ = 2


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name


class Homework(db.Model):
    """Model representing a homework which can be assigned to a submission."""
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    date_due = db.Column(db.Date)

    lesson = db.relationship('Lesson', backref=db.backref('homework', lazy='dynamic'))

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.HOMEWORK.value,
        'polymorphic_on': type_id
    }

    def __init__(self, lesson_id, title, description, type_id, date_due):
        self.lesson_id = lesson_id
        self.title = title
        self.description = description
        self.type_id = type_id
        self.date_due = date_due

    def to_dict(self, date_as_string=False):
        return {
            'lesson_id': self.lesson_id,
            'title': self.title,
            'description': self.description,
            'type': HomeworkType(self.type_id).name,
            'date_due': self.date_due.strftime('%d/%m/%Y') if date_as_string else self.date_due
        }


class Quiz(Homework):
    id = db.Column(db.Integer, db.ForeignKey('homework.id'), primary_key=True)
    number_of_questions = db.Column(db.Integer)

    questions = db.relationship('Question', backref='quiz', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.QUIZ.value,
    }

    def __init__(self, lesson_id, title, description, type_id, date_due, number_of_questions):
        super().__init__(lesson_id, title, description, type_id, date_due)
        self.number_of_questions = number_of_questions

    def to_dict(self, date_as_string=False):
        dictionary = super().to_dict(date_as_string)
        dictionary['number_of_questions'] = self.number_of_questions
        dictionary['questions'] = [q.to_dict() for q in self.questions]
        return dictionary


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    datetime_submitted = db.Column(db.DateTime)

    homework = db.relationship('Homework', backref=db.backref('submissions'))

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.HOMEWORK.value,
        'polymorphic_on': type_id
    }


class EssaySubmission(Submission):
    id = db.Column(db.Integer, db.ForeignKey('submission.id'), primary_key=True)
    text = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.ESSAY.value,
    }


class QuizSubmission(Submission):
    id = db.Column(db.Integer, db.ForeignKey('submission.id'), primary_key=True)
    total_score = db.Column(db.Integer)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'))
    question_text = db.Column(db.String(120))
    question_answer = db.Column(db.String(120))

    def __init__(self, homework_id, question_text, question_answer):
        self.homework_id = homework_id
        self.question_answer = question_answer
        self.question_text = question_text

    def to_dict(self):
        return {
            'homework_id': self.homework_id,
            'question_text': self.question_text,
            'answer': self.question_answer
        }


class QuizAnswer(db.Model):
    __table_args__ = (
        db.UniqueConstraint("submission_id", "question_id"),
    )
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(120))
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

