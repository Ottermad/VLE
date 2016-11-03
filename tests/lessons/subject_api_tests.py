import json

from faker import Faker

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from .factories import SubjectFactory

from app.lessons.models import Subject


fake = Faker()


class SubjectAPITestCase(APITestCase):
    def setUp(self):
        super(SubjectAPITestCase, self).setUp()
        self.school_factory = SchoolFactory()
        self.user_factory = UserFactory()
        self.school = self.school_factory.new_into_db()
        self.user = self.user_factory.new_into_db(
            school_id=self.school.id,
            permissions=['Administrator']
        )
        self.subject_factory = SubjectFactory(self.school)

    def tearDown(self):
        super(SubjectAPITestCase, self).tearDown()

    def test_create_subject(self):
        subject = self.subject_factory.new()

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.post(
            '/lessons/subject',
            data=json.dumps(subject.to_dict()),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'JWT ' + token
            }
        )

        self.assertEqual(response.status_code, 201)

        subject_from_db = Subject.query.filter_by(
            name=subject.name, school_id=self.school.id).first()

        self.assertIsNotNone(subject_from_db)

    def test_list_subjects(self):
        # Create subject
        subject = self.subject_factory.new_into_db()

        # Get JWT token needed
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        # Send request and get response
        response = self.client.get(
            '/lessons/subject',
            headers={'Authorization': 'JWT ' + token}
        )

        # Check response status code is 200
        self.assertEqual(response.status_code, 200)

        # Parse json returned
        # response.data is a bytes not a string so needs to be converted
        json_data = json.loads(response.data.decode('utf-8'))

        # Make sure JSON returned has the key subjects
        self.assertIn('subjects', json_data.keys())

        # Make sure our subject is in data returned
        self.assertIn(subject.to_dict(), json_data['subjects'])

    def test_subject_detail(self):
        # Create subject
        subject = self.subject_factory.new_into_db()

        # Get JWT token needed
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        # Send request and get response
        response = self.client.get(
            '/lessons/subject/{}'.format(subject.id),
            headers={'Authorization': 'JWT ' + token}
        )

        # Check response status code is 200
        self.assertEqual(response.status_code, 200)

        # Parse json returned
        # response.data is a bytes not a string so needs to be converted
        json_data = json.loads(response.data.decode('utf-8'))

        # Make sure JSON returned has the key subject
        self.assertIn('subject', json_data.keys())

        # Make sure our subject is in data returned
        self.assertEqual(subject.to_dict(), json_data['subject'])

    def test_update_subject(self):
        # Create subject
        subject = self.subject_factory.new_into_db()

        # Generate new name
        new_name = 'New Name'

        # Assert names are different
        self.assertNotEqual(subject.name, new_name)

        # Send request
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.put(
            '/lessons/subject/{}'.format(subject.id),
            data=json.dumps({'name': new_name}),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        # Check status code
        self.assertEqual(response.status_code, 200)

        # Check subject updated
        subject = Subject.query.get(subject.id)
        self.assertEqual(subject.name, new_name)

    def test_delete_subject(self):
        # Create subject
        subject = self.subject_factory.new_into_db()

        # Assert that subject is in the database
        subject_from_db = Subject.query.get(subject.id)
        self.assertIsNotNone(subject_from_db)

        # Get JWT token needed
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        # Send request and get response
        response = self.client.delete(
            '/lessons/subject/{}'.format(subject.id),
            headers={'Authorization': 'JWT ' + token}
        )

        # Check response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check subject is no longer in database
        subject_from_db = Subject.query.get(subject.id)
        self.assertIsNone(subject_from_db)
