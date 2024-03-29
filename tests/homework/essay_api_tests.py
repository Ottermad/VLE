import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from tests.lessons.factories import SubjectFactory, LessonFactory
from tests.homework.factories import QuizFactory, EssayFactory, EssaySubmissionFactory

from app.user.models import User
from app.permissions.models import Permission, Role
from app.lessons.models import Lesson


class EssayAPITestCase(APITestCase):
    def setUp(self):
        super(EssayAPITestCase, self).setUp()
        self.school_factory = SchoolFactory()
        self.school = self.school_factory.new_into_db()

        self.user_factory = UserFactory(school=self.school)
        self.user = self.user_factory.new_into_db(
            school_id=self.school.id,
            permissions=['Administrator', 'Teacher', 'Student']
        )

        self.subject_factory = SubjectFactory(self.school)
        self.lesson_factory = LessonFactory(self.school)
        self.essay_factory = EssayFactory(self.school)
        self.essay_submission_factory = EssaySubmissionFactory(self.school)

    def tearDown(self):
        super(EssayAPITestCase, self).tearDown()

    def test_essay_create(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        lesson = self.lesson_factory.new_into_db(teachers=[self.user])
        essay = self.essay_factory.new(lesson.id)

        essay_json = essay.to_dict(date_as_string=True)

        response = self.client.post(
            '/homework/essay',
            data=json.dumps(essay_json),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 201)

    def test_essay_submit(self):
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        lesson = self.lesson_factory.new_into_db(students=[self.user])
        essay = self.essay_factory.new_into_db(lesson_id=lesson.id)

        essay_content = "Hello World This is my essay."

        response = self.client.post(
            '/homework/essay/{}'.format(essay.id),
            data=json.dumps({'content': essay_content}),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 201)

    def test_essay_detail(self):
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        lesson = self.lesson_factory.new_into_db(students=[self.user])
        essay = self.essay_factory.new_into_db(lesson_id=lesson.id)


        response = self.client.get(
            '/homework/essay/{}'.format(essay.id),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIn('essay', json_response.keys())
        self.assertEqual(essay.id, json_response['essay']['id'])

    def test_view_essay_submission(self):
        token = self.get_auth_token(self.user.username, self.user.raw_password)

        essay = self.essay_factory.new_into_db()
        submission = self.essay_submission_factory.new_into_db()

        response = self.client.get(
            '/homework/essay/submission/{}'.format(submission.id),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIn('submission', json_response.keys())
        self.assertEqual(submission.id, json_response['submission']['id'])
