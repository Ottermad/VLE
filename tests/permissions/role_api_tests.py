import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from .factories import PermissionFactory, RoleFactory

from app.user.models import User
from app.permissions.models import Permission, Role

school_factory = SchoolFactory()
user_factory = UserFactory()
permission_factory = PermissionFactory()
role_factory = RoleFactory()


class RoleAPITestCase(APITestCase):
    def setUp(self):
        super(RoleAPITestCase, self).setUp()
        self.school = school_factory.new_into_db()
        self.user = user_factory.new_into_db(school_id=self.school.id, permissions=['CRUD_USERS', 'CRUD_PERMISSIONS'])

    def tearDown(self):
        super(RoleAPITestCase, self).tearDown()

    def test_role_create(self):
        role = role_factory.new(school_id=self.school.id)
        permissions = [permission_factory.new_into_db(school_id=self.school.id) for i in range(0, 3)]

        json_data = {
            'name': role.name,
            'permissions': [p.id for p in permissions]
        }

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.post(
            '/permissions/role',
            data=json.dumps(json_data),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 201)

        role_from_db = Role.query.filter_by(name=role.name, school_id=self.school.id).first()
        self.assertIsNotNone(role_from_db)

        role_permission_ids = [p.id for p in role_from_db.permissions]

        for permission in permissions:
            self.assertIn(permission.id, role_permission_ids)
