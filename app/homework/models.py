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

    def has_submitted(self, user_id):
        submission = Submission.query.filter_by(user_id=user_id, homework_id=self.id).first()
        return not (submission is None)

    def __init__(self, lesson_id, title, description, type_id, date_due):
        self.lesson_id = lesson_id
        self.title = title
        self.description = description
        self.type_id = type_id
        self.date_due = date_due

    def to_dict(self, date_as_string=False, nest_lesson=False, has_submitted=False, user_id=None):
        homework_dict = {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'description': self.description,
            'type': HomeworkType(self.type_id).name,
            'date_due': self.date_due.strftime('%d/%m/%Y') if date_as_string else self.date_due
        }

        if nest_lesson:
            homework_dict['lesson'] = self.lesson.to_dict()

        if has_submitted:
            submission = Submission.query.filter_by(user_id=user_id, homework_id=self.id).first()
            has_submitted = not (submission is None)
            homework_dict['submitted'] = has_submitted
            if has_submitted:
                homework_dict['submission'] = submission.to_dict()

        return homework_dict


class Quiz(Homework):
    id = db.Column(db.Integer, db.ForeignKey('homework.id'), primary_key=True)
    number_of_questions = db.Column(db.Integer)

    questions = db.relationship('Question', backref='quiz', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.QUIZ.value,
    }

    def __init__(self, lesson_id, title, description, date_due, number_of_questions):
        super().__init__(lesson_id, title, description, HomeworkType.QUIZ.value, date_due)
        self.number_of_questions = number_of_questions

    def to_dict(self, date_as_string=False, nest_lesson=False, has_submitted=False, user_id=None):
        dictionary = super().to_dict(date_as_string, nest_lesson, has_submitted, user_id)
        dictionary['number_of_questions'] = self.number_of_questions
        dictionary['questions'] = [q.to_dict() for q in self.questions]
        return dictionary


class Essay(Homework):
    id = db.Column(db.Integer, db.ForeignKey('homework.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.ESSAY.value
    }

    def __init__(self, lesson_id, title, description, date_due):
        super().__init__(lesson_id, title,description, HomeworkType.ESSAY.value, date_due)


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    datetime_submitted = db.Column(db.DateTime)

    homework = db.relationship('Homework', backref=db.backref('submissions'))
    comments = db.relationship('Comment', backref=db.backref('submission'))
    user = db.relationship('User')

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.HOMEWORK.value,
        'polymorphic_on': type_id
    }

    def __init__(self, homework_id, type_id, user_id, datetime_submitted):
        self.homework_id = homework_id
        self.type_id = type_id
        self.user_id = user_id
        self.datetime_submitted = datetime_submitted

    def to_dict(self, nest_user=False, nest_comments=False, nest_homework=False):
        submission_dict = {
            'id': self.id,
            'homework_id': self.homework_id,
            'user_id': self.user_id,
            'type_id': self.type_id,
            'type': HomeworkType(self.type_id).name,
            'datetime_submitted': self.datetime_submitted
        }

        if nest_user:
            submission_dict['user'] = self.user.to_dict()

        if nest_homework:
            submission_dict['homework'] = self.homework.to_dict(has_submitted=True, date_as_string=True)

        if nest_comments:
            submission_dict['comments'] = [c.to_dict(nest_user=True) for c in self.comments]

        return submission_dict


class EssaySubmission(Submission):
    id = db.Column(db.Integer, db.ForeignKey('submission.id'), primary_key=True)
    text = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.ESSAY.value,
    }

    def __init__(self, homework_id, user_id, datetime_submitted, text):
        super().__init__(homework_id, HomeworkType.ESSAY.value, user_id, datetime_submitted)
        self.text = text

    def to_dict(self, **kwargs):
        submission_dict = super().to_dict(**kwargs)
        submission_dict['text'] = self.text
        return submission_dict


class QuizAnswer(db.Model):
    __table_args__ = (
        db.UniqueConstraint("submission_id", "question_id"),
    )
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(120))
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    correct = db.Column(db.Boolean)

    def __init__(self, answer, submission_id, question_id):
        self.answer = answer
        self.submission_id = submission_id
        self.question_id = question_id

    def to_dict(self):
        return {
            'answer': self.answer,
            'id': self.id,
            'submission_id': self.submission_id,
            'question_id': self.question_id,
            'correct': self.correct
        }


class QuizSubmission(Submission):
    id = db.Column(db.Integer, db.ForeignKey('submission.id'), primary_key=True)
    total_score = db.Column(db.Integer)

    answers = db.relationship(QuizAnswer, backref='submission', lazy='dynamic')

    __mapper_args__ = {
        'polymorphic_identity': HomeworkType.QUIZ.value,
    }

    def __init__(self, homework_id, user_id, datetime_submitted):
        super().__init__(homework_id, HomeworkType.QUIZ.value, user_id, datetime_submitted)
        self.total_score = 0

    def mark(self):
        score = 0
        # TODO: Refactor to make more efficient
        for answer in self.answers:
            answer.correct = False
            question = Question.query.get(answer.question_id)
            if question.question_answer == answer.answer:
                score += 1
                answer.correct = True
        self.total_score = score

    def to_dict(self, **kwargs):
        submission_dict = super().to_dict(**kwargs)
        submission_dict['score'] = self.total_score
        submission_dict['answers'] = [answer.to_dict() for answer in self.answers]
        return submission_dict


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
            'answer': self.question_answer,
            'id': self.id
        }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))

    def __init__(self, submission_id, text, user_id):
        self.submission_id = submission_id
        self.text = text
        self.user_id = user_id

    def to_dict(self, nest_user=False):
        dictionary = {
            'id': self.id,
            'submission_id': self.submission_id,
            'text': self.text,
            'user_id': self.user_id
        }
        if nest_user:
            dictionary['user'] = self.user.to_dict()
        return dictionary
