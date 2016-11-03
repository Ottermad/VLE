import unittest
import json

from app import db, create_app

from tests import APITestCase
from tests.school.factories import SchoolFactory

from app.user.models import User
from .factories import UserFactory
from app.user.user_functions import user_listing

user_factory = UserFactory()
school_factory = SchoolFactory()


class UserAPITestCase(APITestCase):
    def setUp(self):
        super(UserAPITestCase, self).setUp()
        self.school = school_factory.new_into_db()
        self.user = user_factory.new_into_db(school_id=self.school.id, permissions=['Administrator'])

    def tearDown(self):
        super(UserAPITestCase, self).tearDown()

    def test_user_listing_with_no_query_params(self):
        # Create dummy users
        users = [user_factory.new_into_db(school_id=self.school.id) for i in range(0,3)]

        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

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

    def test_user_listing_with_nest_roles(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        # Get response
        response = self.client.get(
            '/user/user?nest-roles=true',
            headers={'Authorization': 'JWT ' + token})

        # Convert JSON back to dictionary
        dict_response = json.loads(response.data.decode('utf-8'))

        # Test for success
        self.assertTrue(dict_response['success'])
        self.assertIn('roles', dict_response['users'][0].keys())

    def test_user_listing_with_nest_permissions(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        # Get response
        response = self.client.get(
            '/user/user?nest-permissions=true',
            headers={'Authorization': 'JWT ' + token})

        # Convert JSON back to dictionary
        dict_response = json.loads(response.data.decode('utf-8'))

        # Test for success
        self.assertTrue(dict_response['success'])
        self.assertIn('permissions', dict_response['users'][0].keys())

    def test_user_listing_with_nest_role_permissions(self):
        # Create a user with a role
        user = user_factory.new_into_db(school_id=self.school.id, roles=['ADMINISTRATOR'])

        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        # Get response
        response = self.client.get(
            '/user/user?nest-roles=true&nest-role-permissions=true',
            headers={'Authorization': 'JWT ' + token})

        # Convert JSON back to dictionary
        dict_response = json.loads(response.data.decode('utf-8'))

        # Test for success
        self.assertTrue(dict_response['success'])

        user_found = False
        for user_dict in dict_response['users']:
            if user_dict['username'] == user.username:
                user_found = True
                self.assertIn('roles', user_dict.keys())
                self.assertIn('permissions', user_dict['roles'][0])
        self.assertTrue(user_found)

    def test_user_create_success(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_user = user_factory.new()
        user_dict = mock_user.to_dict()
        user_dict['password'] = mock_user.raw_password

        response = self.client.post(
            '/user/user',
            data=json.dumps(user_dict),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 201)
        user = User.query.filter_by(username=mock_user.username, school_id=mock_user.school_id)
        self.assertIsNotNone(user)
