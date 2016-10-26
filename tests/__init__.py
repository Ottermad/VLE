import unittest

from app import db, create_app

import json


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_auth_token(self, username, password):
        response = self.client.post(
            '/auth',
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'username': username,
                'password': password
            })
        )
        json_response = json.loads(response.data.decode('utf-8'))
        return json_response['access_token']