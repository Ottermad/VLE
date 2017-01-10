import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from tests.lessons.factories import SubjectFactory, LessonFactory
from tests.homework.factories import QuizFactory

from app.user.models import User
from app.permissions.models import Permission, Role
from app.lessons.models import Lesson


class QuizAPITestCase(APITestCase):
    def setUp(self):
        super(QuizAPITestCase, self).setUp()
        self.school_factory = SchoolFactory()
        self.school = self.school_factory.new_into_db()

        self.user_factory = UserFactory(school=self.school)
        self.user = self.user_factory.new_into_db(
            school_id=self.school.id,
            permissions=['Administrator', 'Teacher']
        )

        self.subject_factory = SubjectFactory(self.school)
        self.lesson_factory = LessonFactory(self.school)
        self.quiz_factory = QuizFactory(self.school)

    def tearDown(self):
        super(QuizAPITestCase, self).tearDown()

    def test_quiz_create(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        lesson = self.lesson_factory.new_into_db(teachers=[self.user])
        quiz = self.quiz_factory.new(lesson.id)

        quiz_json = quiz.to_dict(date_as_string=True)

        response = self.client.post(
            '/homework/quiz',
            data=json.dumps(quiz_json),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 201)

