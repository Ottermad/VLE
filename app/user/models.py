from app import db

from flask_bcrypt import generate_password_hash


class User(db.Model):
    """Represents a user."""
    __table_args__ = (
        db.UniqueConstraint('school_id', 'username'),
        {}
    )

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    username = db.Column(db.String(120))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.LargeBinary())

    def __init__(self, username, first_name, last_name, email, password, school_id):
        """Create a User object but not save it to the database."""
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.school_id = school_id

        # Securely hash the password using bcrypt
        self.password = generate_password_hash(password)

    def to_dict(self):
        """Convert instance into a dict, excluding password."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'username': self.username
        }
