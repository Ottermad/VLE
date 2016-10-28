import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory

from app.user.models import User
from app.permissions.models import Permission, Role

school_factory = SchoolFactory()
user_factory = UserFactory()


class APITestCase(APITestCase):
    def setUp(self):
        super(PermissionAPITestCase, self).setUp()
        self.school = school_factory.new_into_db()
        self.user = user_factory.new_into_db(
            school_id=self.school.id,
            permissions=['CRUD_USERS', 'CRUD_PERMISSIONS']
        )

    def tearDown(self):
        super(PermissionAPITestCase, self).tearDown()