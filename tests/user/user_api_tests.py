import unittest
import json

from app import db, create_app

from tests import APITestCase
from tests.school.factories import SchoolFactory

from app.user.models import User
from tests.user.factories import UserFactory, FormFactory
from app.user.user_functions import user_listing

user_factory = UserFactory()
school_factory = SchoolFactory()
form_factory = FormFactory()


class UserAPITestCase(APITestCase):
    def setUp(self):
        super(UserAPITestCase, self).setUp()
        self.school = school_factory.new_into_db()
        self.user = user_factory.new_into_db(school_id=self.school.id, permissions=['Administrator'])
        self.form = form_factory.new_into_db(school_id=self.school.id)

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

    def test_user_create_success(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_user = user_factory.new(school_id=self.school.id)
        user_dict = mock_user.to_dict()
        user_dict['password'] = mock_user.raw_password
        del user_dict['form_id']

        response = self.client.post(
            '/user/user',
            data=json.dumps(user_dict),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )
        import ipdb
        self.assertEqual(response.status_code, 201)
        user = User.query.filter_by(username=mock_user.username, school_id=mock_user.school_id)
        self.assertIsNotNone(user)

    def test_user_create_failed_duplicate_email(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_user = user_factory.new(school_id=self.school.id)
        mock_user2 = user_factory.new_into_db(school_id=self.school.id)
        user_dict = mock_user.to_dict()
        user_dict['password'] = mock_user.raw_password
        user_dict['email'] = mock_user2.email

        response = self.client.post(
            '/user/user',
            data=json.dumps(user_dict),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 409)

    def test_user_create_failed_blank_values(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_user = user_factory.new(school_id=self.school.id)
        user_dict = mock_user.to_dict()
        for key in user_dict.keys():
            user_dict[key] = ""

        response = self.client.post(
            '/user/user',
            data=json.dumps(user_dict),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 409)

    def test_user_create_failed_missing_keys(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.post(
            '/user/user',
            data=json.dumps({}),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 409)

    def test_user_edit_success(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_user = user_factory.new_into_db(school_id=self.school.id)
        user_dict = {}
        user_dict['first_name'] = 'Charles' if mock_user.first_name != "Charles" else "Charlie"

        response = self.client.put(
            '/user/user/{}'.format(mock_user.id),
            data=json.dumps(user_dict),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username=mock_user.username, school_id=mock_user.school_id).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, user_dict['first_name'])

    def test_user_edit_failed_bad_id(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.put(
            '/user/user/{}'.format(-1),
            data=json.dumps({}),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 404)

    def test_user_edit_failed_duplicate_email(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_user = user_factory.new_into_db(school_id=self.school.id)
        mock_user2 = user_factory.new_into_db(school_id=self.school.id)
        user_dict = mock_user.to_dict()
        user_dict['password'] = mock_user.raw_password
        user_dict['email'] = mock_user2.email

        response = self.client.put(
            '/user/user/{}'.format(mock_user.id),
            data=json.dumps(user_dict),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 409)

    def test_user_edit_failed_blank_values(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_user = user_factory.new_into_db(school_id=self.school.id)
        user_dict = mock_user.to_dict()
        for key in user_dict.keys():
            user_dict[key] = ""

        response = self.client.put(
            '/user/user/{}'.format(mock_user.id),
            data=json.dumps(user_dict),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 409)

    def test_user_delete_success(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_user = user_factory.new_into_db(school_id=self.school.id)
        response = self.client.delete(
            '/user/user/{}'.format(mock_user.id),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username=mock_user.username).first()
        self.assertIsNone(user)

    def test_user_delete_failed_bad_id(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_user = user_factory.new_into_db(school_id=self.school.id)
        response = self.client.delete(
            '/user/user/-1',
            headers = {'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 404)
        user = User.query.filter_by(username=mock_user.username).first()
        self.assertIsNotNone(user)

