import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from .factories import SubjectFactory, LessonFactory

from app.user.models import User
from app.permissions.models import Permission, Role
from app.lessons.models import Lesson


class LessonAPITestCase(APITestCase):
    def setUp(self):
        super(LessonAPITestCase, self).setUp()
        self.school_factory = SchoolFactory()
        self.school = self.school_factory.new_into_db()

        self.user_factory = UserFactory(school=self.school)
        self.user = self.user_factory.new_into_db(
            school_id=self.school.id,
            permissions=['Administrator']
        )

        self.subject_factory = SubjectFactory(self.school)
        self.lesson_factory = LessonFactory(self.school)

    def tearDown(self):
        super(LessonAPITestCase, self).tearDown()

    def test_lesson_create(self):
        lesson = self.lesson_factory.new()
        lesson.teachers = [self.user_factory.new_into_db() for i in range(0, 3)]
        lesson.students = [self.user_factory.new_into_db() for i in range(0, 3)]

        lesson_as_json = lesson.to_dict()
        lesson_as_json['teacher_ids'] = [t.id for t in lesson.teachers]
        lesson_as_json['student_ids'] = [s.id for s in lesson.students]

        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        response = self.client.post(
            '/lessons/lesson',
            data=json.dumps(lesson_as_json),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 201)

        lesson_from_db = Lesson.query.filter_by(name=lesson.name, school_id=lesson.school_id).first()
        self.assertIsNotNone(lesson_from_db)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertIn('lesson', json_response.keys())
        self.assertIn('teachers', json_response['lesson'].keys())
        for teacher in lesson.teachers:
            self.assertIn(teacher.to_dict(), json_response['lesson']['teachers'])

        self.assertIn('students', json_response['lesson'].keys())
        for student in lesson.students:
            self.assertIn(student.to_dict(), json_response['lesson']['students'])

    def test_lesson_listing(self):
        lessons = [self.lesson_factory.new_into_db()]

        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        response = self.client.get(
            '/lessons/lesson',
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertIn('lessons', json_response.keys())

        for lesson in lessons:
            self.assertIn(lesson.to_dict(), json_response['lessons'])


