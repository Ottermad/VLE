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
        self.user_factory.new_into_db()
        for i in range(0, 3):
            # lesson.teachers.append(self.user_factory.new_into_db())
            # lesson.students.append(self.user_factory.new_into_db())
            pass

        lesson_as_json = lesson.to_dict()

        lesson_as_json['teacher_ids'] = [self.user_factory.new_into_db().id for i in range(0, 3)]
        lesson_as_json['student_ids'] = [self.user_factory.new_into_db().id for i in range(0, 3)]

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
        for teacher_id in lesson_as_json['teacher_ids']:
            teacher = User.query.get(teacher_id)
            self.assertIn(teacher.to_dict(), json_response['lesson']['teachers'])

        self.assertIn('students', json_response['lesson'].keys())
        for student_id in lesson_as_json['student_ids']:
            student = User.query.get(student_id)
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

    def test_lesson_listing_with_subject(self):
        subject1 = self.subject_factory.new_into_db()
        subject2 = self.subject_factory.new_into_db()

        lesson1 = self.lesson_factory.new_into_db(subject=subject1)
        lesson2 = self.lesson_factory.new_into_db(subject=subject2)

        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        response = self.client.get(
            '/lessons/lesson?subject={}'.format(subject1.id),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertIn('lessons', json_response.keys())

        self.assertIn(lesson1.to_dict(), json_response['lessons'])
        self.assertNotIn(lesson2.to_dict(), json_response['lessons'])

    def test_lesson_detail(self):
        lesson = self.lesson_factory.new_into_db()

        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        response = self.client.get(
            '/lessons/lesson/{}'.format(lesson.id),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertIn('lesson', json_response.keys())

        # Make sure our lesson is in data returned
        self.assertEqual(lesson.to_dict(), json_response['lesson'])

    def test_lesson_delete(self):
        lesson = self.lesson_factory.new_into_db()

        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        response = self.client.delete(
            '/lessons/lesson/{}'.format(lesson.id),
            headers={'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)

        lesson_from_db = Lesson.query.get(lesson.id)
        self.assertIsNone(lesson_from_db)

    def test_lesson_update(self):
        lesson = self.lesson_factory.new_into_db()

        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)

        json_update = {}
        json_update['name'] = "new_name" if lesson.name != "new_name" else "another_name"
        json_update['teacher_ids'] = [self.user_factory.new_into_db().id for i in range(0, 3)]
        json_update['student_ids'] = [self.user_factory.new_into_db().id for i in range(0, 3)]
        json_update['subject_id'] = self.subject_factory.new_into_db().id

        response = self.client.put(
            '/lessons/lesson/{}'.format(lesson.id),
            data=json.dumps(json_update),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)

        lesson_from_db = Lesson.query.get(lesson.id)
        self.assertIsNotNone(lesson_from_db)

        self.assertEqual(lesson_from_db.name, json_update['name'])
        self.assertEqual(lesson_from_db.subject_id, json_update['subject_id'])
        self.assertEqual([t.id for t in lesson_from_db.teachers], json_update['teacher_ids'])
        self.assertEqual([s.id for s in lesson_from_db.students], json_update['student_ids'])


