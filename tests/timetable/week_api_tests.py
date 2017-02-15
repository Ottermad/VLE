import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from tests.timetable.factories import PeriodFactory, WeekFactory

from app.user.models import User
from app.permissions.models import Permission, Role
from app.lessons.models import Lesson


class WeekAPITestCase(APITestCase):
    def setUp(self):
        super(WeekAPITestCase, self).setUp()
        self.school_factory = SchoolFactory()
        self.school = self.school_factory.new_into_db()

        self.user_factory = UserFactory(school=self.school)
        self.user = self.user_factory.new_into_db(
            school_id=self.school.id,
            permissions=['Administrator', 'Teacher', 'Student']
        )

        self.week_factory = WeekFactory(school=self.school)
        self.period_factory = PeriodFactory(school=self.school)

    def tearDown(self):
        super(WeekAPITestCase, self).tearDown()

    def test_week_create(self):
        token = self.get_auth_token(username=self.user.username, password=self.user.raw_password)
        week = self.week_factory.new()

        response = self.client.post(
            '/timetable/week',
            data=json.dumps({'name': week.name}),
            headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 201)

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['name'], week.name)
        self.assertEqual(json_response['school_id'], week.school_id)
