import json

from tests import APITestCase
from tests.school.factories import SchoolFactory

from tests.user.factories import UserFactory

user_factory = UserFactory()
school_factory = SchoolFactory()


class SchoolAPITestCase(APITestCase):
    def setUp(self):
        super(SchoolAPITestCase, self).setUp()

    def tearDown(self):
        super(SchoolAPITestCase, self).tearDown()

    def test_success(self):
        school = school_factory.new()
        user = user_factory.new()

        dictionary = user.to_dict()
        dictionary['password'] = user.raw_password
        dictionary['school_name'] = school.name

        # Get response
        response = self.client.post(
            '/school/signup',
            data=json.dumps(dictionary),
            headers={'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)

    def test_failed_due_to_missing_keys(self):
        data = {}

        # Get response
        response = self.client.post(
            '/school/signup',
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 409)

    def test_failed_due_to_blank(self):
        data = {
            'first_name': '',
            'last_name': '',
            'username': '',
            'password': '',
            'email': '',
            'school_name': ''
        }

        # Get response
        response = self.client.post(
            '/school/signup',
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 409)

    def test_failed_due_to_duplicate_username(self):
        school = school_factory.new_into_db()
        user = user_factory.new_into_db(school_id=school.id)

        duplicate_user = user_factory.new()
        duplicate_user.username = user.username
        school = school_factory.new()
        data = duplicate_user.to_dict()
        data['school_name'] = school.name

        # Get response
        response = self.client.post(
            '/school/signup',
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 409)

    def test_failed_due_to_duplicate_email(self):
        school = school_factory.new_into_db()
        user = user_factory.new_into_db(school_id=school.id)

        duplicate_user = user_factory.new()
        duplicate_user.email = user.email
        school = school_factory.new()
        data = duplicate_user.to_dict()
        data['school_name'] = school.name

        # Get response
        response = self.client.post(
            '/school/signup',
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 409)