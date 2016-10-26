from app import db


lesson_teacher = db.Table(
    'lesson_teacher',
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

lesson_student = db.Table(
    'lesson_student',
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name):
        self.name = name


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    teachers = db.relationship(
        'User', secondary=lesson_teacher,
        backref=db.backref('lesson_teacher', lazy='dynamic')
    )

    students = db.relationship(
        'User', secondary=lesson_student,
        backref=db.backref('lesson_student', lazy='dynamic')
    )

    def __init__(self, name, subject_id):
        self.name = name
        self.subject = subject_id

