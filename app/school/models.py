from app import db


class School(db.Model):
    """Model representing a school."""

    id = db.Column(db.Integer, primary_key=True)  # Represents id column
    name = db.Column(db.String(120), unique=True)  # Represents name column

    def __init__(self, school_name):
        """Constructor"""
        self.name = school_name

    def to_dict(self):
        """Converts School object into dictionary."""
        return {
            "id": self.id,
            "name": self.name
        }