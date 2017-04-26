import unittest

from app import db, create_app

from tests.school.factories import SchoolFactory

from app.user.models import User
from tests.user.factories import UserFactory

user_factory = UserFactory()
school_factory = SchoolFactory()


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.school = school_factory.new_into_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


    # def test_creation(self):
    #     """Test users can be added to the database correctly."""
    #     user = user_factory.new()
    #
    #     db.session.add(user)
    #     db.session.commit()
    #
    #     user_from_db = User.query.filter_by(username=user.username).first()
    #     self.assertIsNotNone(user_from_db)