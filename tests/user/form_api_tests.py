import unittest
import json

from app import db, create_app

from tests import APITestCase
from tests.school.factories import SchoolFactory

from app.user.models import Form
from tests.user.factories import FormFactory, UserFactory

school_factory = SchoolFactory()
form_factory = FormFactory()
user_factory = UserFactory()


class UserAPITestCase(APITestCase):
    def setUp(self):
        super(UserAPITestCase, self).setUp()
        self.school = school_factory.new_into_db()
        self.user = user_factory.new_into_db(school_id=self.school.id, permissions=['Administrator'])
        self.form = form_factory.new_into_db(school_id=self.school.id)

    def tearDown(self):
        super(UserAPITestCase, self).tearDown()

    def test_form_listing(self):
        # Create dummy forms
        forms = [form_factory.new_into_db(school_id=self.school.id) for i in range(0,3)]

        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        # Get response
        response = self.client.get(
            '/user/form',
            headers={'Authorization': 'JWT ' + token})

        # Convert JSON back to dictionary
        dict_response = json.loads(response.data.decode('utf-8'))


        # Test for success
        self.assertTrue(dict_response['success'])
        for form in forms:
            self.assertIn(form.to_dict(), dict_response['forms'])

    def test_form_create_success(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_form = form_factory.new(school_id=self.school.id)
        form_dict = mock_form.to_dict()

        response = self.client.post(
            '/user/form',
            data=json.dumps(form_dict),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 201)
        form = Form.query.filter_by(name=mock_form.name, school_id=mock_form.school_id)
        self.assertIsNotNone(form)

    def test_form_edit_success(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_form = form_factory.new_into_db(school_id=self.school.id)
        form_dict = {}
        form_dict['name'] = 'Charles' if mock_form.name != "Charles" else "Charlie"

        response = self.client.put(
            '/user/form/{}'.format(mock_form.id),
            data=json.dumps(form_dict),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)
        form = Form.query.filter_by(name=mock_form.name, school_id=mock_form.school_id).first()
        self.assertIsNotNone(form)
        self.assertEqual(form.name, form_dict['name'])

    def test_form_delete_success(self):
        # Get an auth token
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        mock_form = form_factory.new_into_db(school_id=self.school.id)
        response = self.client.delete(
            '/user/form/{}'.format(mock_form.id),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)
        form = Form.query.filter_by(name=mock_form.name).first()
        self.assertIsNone(form)