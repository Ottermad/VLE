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


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))

    teachers = db.relationship(
        'User', secondary=lesson_teacher,
        backref=db.backref('lesson_teacher', lazy='dynamic')
    )

    students = db.relationship(
        'User', secondary=lesson_student,
        backref=db.backref('lesson_student', lazy='dynamic')
    )

    def __init__(self, name, subject_id, school_id):
        self.name = name
        self.subject = subject_id
        self.school_id = school_id

    def to_dict(self, nest_teachers=False, nest_students=False):
        lesson_as_dict = {
            'id': self.id,
            'name': self.name,
            'school_id': self.school_id
        }

        if nest_teachers:
            lesson_as_dict['teachers'] = [t.to_dict() for t in self.teachers]

        if nest_students:
            lesson_as_dict['students'] = [s.to_dict() for s in self.students]

        return lesson_as_dict
