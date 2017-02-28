import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory


user_factory = UserFactory()
school_factory = SchoolFactory()


class LoginAPITestCase(APITestCase):
    def setUp(self):
        super(LoginAPITestCase, self).setUp()
        self.school = school_factory.new_into_db()
        self.user = user_factory.new_into_db(school_id=self.school.id, permissions=['Administrator'])

    def tearDown(self):
        super(LoginAPITestCase, self).tearDown()

    def test_login_user_success(self):
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
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIn("access_token", json_response.keys())

    def test_login_failed_due_to_incorrect_password(self):
        password = 'test1' if self.user.raw_password != 'test1' else 'test2'
        response = self.client.post(
            '/auth',
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'username': self.user.username,
                'password': password
            })
        )
        self.assertEqual(response.status_code, 401)

    def test_login_failed_due_to_incorrect_username(self):
        username = 'test1' if self.user.username != 'test1' else 'test2'
        response = self.client.post(
            '/auth',
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'username': username,
                'password': self.user.raw_password
            })
        )
        self.assertEqual(response.status_code, 401)