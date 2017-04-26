import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from tests.lessons.factories import SubjectFactory, LessonFactory
from tests.homework.factories import QuizFactory, EssayFactory, EssaySubmissionFactory, CommentFactory

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

        self.comment_factory = CommentFactory(self.school)
        self.essay_factory = EssayFactory(self.school)
        self.lesson_factory = LessonFactory(self.school)
        self.essay_submission_factory = EssaySubmissionFactory(self.school)

    def tearDown(self):
        super(EssayAPITestCase, self).tearDown()

    def test_comment_create(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        lesson = self.lesson_factory.new_into_db(teachers=[self.user])
        essay = self.essay_factory.new_into_db(lesson_id=lesson.id)
        submission = self.essay_submission_factory.new_into_db(essay=essay)
        comment = self.comment_factory.new(submission_id=submission.id, user_id=self.user.id)

        comment_json = comment.to_dict()

        response = self.client.post(
            '/homework/comment',
            data=json.dumps(comment_json),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 201)

    def test_comment_delete(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        comment = self.comment_factory.new_into_db()

        response = self.client.delete(
            '/homework/comment/{}'.format(comment.id),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)
