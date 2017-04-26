from app import db


from flask_bcrypt import generate_password_hash
from app.permissions.models import user_roles, user_permissions
from app.lessons.models import lesson_student, lesson_teacher


class User(db.Model):
    """Represents a user."""
    __table_args__ = (
        db.UniqueConstraint('school_id', 'username'),
        {}
    )

    # Generic properties
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    username = db.Column(db.String(120))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.LargeBinary())
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=True)

    form = db.relationship('Form', backref=db.backref('form', lazy='dynamic'))

    # Permissions and Roles
    permissions = db.relationship(
        'Permission', secondary=user_permissions,
        backref=db.backref('user_permissions', lazy='dynamic')
    )
    roles = db.relationship(
        'Role', secondary=user_roles,
        backref=db.backref('user_roles', lazy='dynamic')
    )

    # Lessons
    lessons_taught = db.relationship(
        'Lesson', secondary=lesson_teacher,
        passive_deletes=True,
        # backref=db.backref('lesson_teacher', lazy='dynamic')
    )

    lessons_attending = db.relationship(
        'Lesson', secondary=lesson_student,
        passive_deletes=True,
        # backref=db.backref('lesson_student', lazy='dynamic')
    )

    def __init__(self, username, first_name, last_name, email, password, school_id, form_id=None):
        """Create a User object but not save it to the database."""
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.school_id = school_id
        self.form_id = form_id

        # Securely hash the password using bcrypt
        self.password = self.generate_password_hash(password)

    @classmethod
    def generate_password_hash(self, password):
        return generate_password_hash(password)

    def to_dict(self, nest_roles=False, nest_role_permissions=False, nest_permissions=False, nest_form=False):
        """Convert instance into a dict, excluding password."""
        user_dictionary = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'username': self.username,
            'school_id': self.school_id,
            'form_id': self.form_id
        }
        if nest_roles:
            user_dictionary['roles'] = [r.to_dict(nest_permissions=nest_role_permissions) for r in self.roles]

        if nest_permissions:
            user_dictionary['permissions'] = [p.to_dict() for p in self.permissions]

        if nest_form and self.form is not None:
            user_dictionary['form'] = self.form.to_dict()

        return user_dictionary

    def has_permissions(self, permissions, include_roles=True):
        users_permissions = {permission.name for permission in self.permissions}

        if include_roles:
            for role in self.roles:
                for permission in role.permissions:
                    users_permissions.add(permission.name)
        return permissions.issubset(users_permissions)

    def has_roles(self, roles):
        users_roles = {role.name for role in self.roles}
        return roles.issubset(users_roles)


class Form(db.Model):
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
