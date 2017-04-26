import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from tests.lessons.factories import SubjectFactory, LessonFactory
from tests.homework.factories import QuizFactory, EssaySubmissionFactory, QuizSubmissionFactory

from app.user.models import User
from app.permissions.models import Permission, Role
from app.lessons.models import Lesson


class HomeworkAPITestCase(APITestCase):
    def setUp(self):
        super(HomeworkAPITestCase, self).setUp()
        self.school_factory = SchoolFactory()
        self.school = self.school_factory.new_into_db()

        self.user_factory = UserFactory(school=self.school)
        self.user = self.user_factory.new_into_db(
            school_id=self.school.id,
            permissions=['Administrator', 'Teacher', 'Student']
        )

        self.subject_factory = SubjectFactory(self.school)
        self.lesson_factory = LessonFactory(self.school)
        self.quiz_factory = QuizFactory(self.school)
        self.essay_submission_factory = EssaySubmissionFactory(self.school)
        self.quiz_submission_factory = QuizSubmissionFactory(self.school)

    def tearDown(self):
        super(HomeworkAPITestCase, self).tearDown()

    def test_submission_listing_for_students(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        submission = self.essay_submission_factory.new_into_db(user_id=self.user.id)

        response = self.client.get(
            '/homework/submissions',
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIn('submissions', json_response.keys())

        self.assertIn(submission.id, [s['id'] for s in json_response['submissions']])

    def test_submission_listing_for_homework(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        quiz = self.quiz_factory.new_into_db()
        submission = self.quiz_submission_factory.new_into_db(quiz=quiz)

        response = self.client.get(
            '/homework/homework/{}/submissions'.format(quiz.id),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIn('submissions', json_response.keys())

        self.assertIn(submission.id, [s['id'] for s in json_response['submissions']])

    def test_submission_listing_for_homework_failed_bad_id(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        response = self.client.get(
            '/homework/homework/{}/submissions'.format(-1),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 404)

    def test_list_homework_for_lesson(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)
        quiz = self.quiz_factory.new_into_db()

        response = self.client.get(
            '/homework/due/{}'.format(quiz.lesson.id),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIn('homework', json_response.keys())

        self.assertIn(quiz.id, [h['id'] for h in json_response['homework']])

    def test_list_homework_for_lesson_failed_bad_id(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        response = self.client.get(
            '/homework/due/{}'.format(-1),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 404)

    def test_homework_summary(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        lesson = self.lesson_factory.new_into_db(students=[self.user])
        quiz = self.quiz_factory.new_into_db(lesson_id=lesson.id)

        response = self.client.get(
            '/homework/summary',
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIn('homework', json_response.keys())

        self.assertIn(quiz.id, [h['id'] for h in json_response['homework']])
