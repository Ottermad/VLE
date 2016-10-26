import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory

from app.user.models import User
from app.permissions.models import Permission, Role

school_factory = SchoolFactory()
user_factory = UserFactory()


class PermissionAPITestCase(APITestCase):
    def setUp(self):
        super(PermissionAPITestCase, self).setUp()
        self.school = school_factory.new_into_db(without_roles=True, without_permissions=True)
        self.user = user_factory.new_into_db(school_id=self.school.id, permissions=['CRUD_USERS'])

    def tearDown(self):
        super(PermissionAPITestCase, self).tearDown()

    def test_set_defaults(self):
        school = school_factory.new_into_db(without_roles=True, without_permissions=True)
        user = user_factory.new_into_db(school_id=school.id)

        token = self.get_auth_token(user.username, user.raw_password)

        response = self.client.post(
            '/permissions/set-defaults',
            headers={'Authorization': 'JWT ' + token})

        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['success'])

        permission_query = Permission.query.filter_by(school_id=school.id)
        self.assertIsNotNone(permission_query.first())

        role_query = Role.query.filter_by(school_id=school.id)
        self.assertIsNotNone(role_query.first())

        user_from_db = User.query.get(user.id)
        self.assertIsNotNone(user_from_db)
        role_names = [role.name for role in user_from_db.roles]
        self.assertIn('ADMINISTRATOR', role_names)
