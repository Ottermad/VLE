import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from .factories import SubjectFactory

from app.lessons.models import Subject


class SubjectAPITestCase(APITestCase):
    def setUp(self):
        super(SubjectAPITestCase, self).setUp()
        self.school_factory = SchoolFactory()
        self.user_factory = UserFactory()
        self.school = self.school_factory.new_into_db()
        self.user = self.user_factory.new_into_db(
            school_id=self.school.id,
            permissions=['CRUD_USERS', 'CRUD_PERMISSIONS']
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
        pass

    def test_subject_detail(self):
        pass

    def test_update_subject(self):
        pass

    def test_delete_subject(self):
        pass
