import unittest
import json

from app import db, create_app

from tests.school.factories import SchoolFactory

from app.user.models import User
from .factories import UserFactory
from app.user.user_functions import user_listing

user_factory = UserFactory()
school_factory = SchoolFactory()


class MockRequest:
    def __init__(self):
        self.args = {}




class UserViewsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.school = school_factory.new_into_db()
        self.user = user_factory.new_into_db(school_id=self.school.id, permissions=['CRUD_USERS'])


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_auth_token(self):
        response = self.client.post(
            '/auth',
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'username': self.user.username,
                'password': self.user.raw_password
            })
        )
        json_response = json.loads(response.data.decode('utf-8'))
        return json_response['access_token']

    def test_user_listing_with_no_query_params(self):
        # Create dummy users
        users = [user_factory.new_into_db(school_id=self.school.id) for i in range(0,3)]

        # Get an auth token
        token = self.get_auth_token()

        # Get response
        response = self.client.get(
            '/user/user',
            headers={'Authorization': 'JWT ' + token})

        # Convert JSON back to dictionary
        dict_response = json.loads(response.data.decode('utf-8'))


        # Test for success
        self.assertTrue(dict_response['success'])
        for user in users:
            self.assertIn(user.to_dict(), dict_response['users'])
