from app import db


class School(db.Model):
    """Model representing a school."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)

    def __init__(self, school_name):
        self.name = school_name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }