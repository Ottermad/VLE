import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from tests.permissions.factories import PermissionFactory, RoleFactory

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
        self.user = user_factory.new_into_db(school_id=self.school.id, permissions=['Administrator'])

    def tearDown(self):
        super(RoleAPITestCase, self).tearDown()

    # def test_role_create(self):
    #     role = role_factory.new(school_id=self.school.id)
    #     permissions = [permission_factory.new_into_db(school_id=self.school.id) for i in range(0, 3)]
    #
    #     json_data = {
    #         'name': role.name,
    #         'permissions': [p.id for p in permissions]
    #     }
    #
    #     token = self.get_auth_token(self.user.username, self.user.raw_password)
    #
    #     response = self.client.post(
    #         '/permissions/role',
    #         data=json.dumps(json_data),
    #         headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
    #     )
    #
    #     self.assertEqual(response.status_code, 201)
    #
    #     role_from_db = Role.query.filter_by(name=role.name, school_id=self.school.id).first()
    #     self.assertIsNotNone(role_from_db)
    #
    #     role_permission_ids = [p.id for p in role_from_db.permissions]
    #
    #     for permission in permissions:
    #         self.assertIn(permission.id, role_permission_ids)
    #
    # def test_role_listing(self):
    #     roles = [role_factory.new_into_db(school_id=self.school.id) for i in range(0, 3)]
    #
    #     token = self.get_auth_token(self.user.username, self.user.raw_password)
    #
    #     response = self.client.get(
    #         '/permissions/role',
    #         headers={'Authorization': 'JWT ' + token}
    #     )
    #
    #     self.assertEqual(response.status_code, 200)
    #
    #     json_response = json.loads(response.data.decode('utf-8'))
    #
    #     self.assertIn('roles', json_response.keys())
    #
    #     for role in roles:
    #         self.assertIn(role.to_dict(nest_permissions=True), json_response['roles'])
    #
    # def test_role_detail(self):
    #     role = role_factory.new_into_db(school_id=self.school.id)
    #     token = self.get_auth_token(self.user.username, self.user.raw_password)
    #
    #     response = self.client.get(
    #         '/permissions/role/{}'.format(role.id),
    #         headers={'Authorization': 'JWT ' + token}
    #     )
    #
    #     self.assertEqual(response.status_code, 200)
    #
    #     json_response = json.loads(response.data.decode('utf-8'))
    #
    #     self.assertIn('role', json_response.keys())
    #
    #     self.assertEqual(role.to_dict(nest_permissions=True), json_response['role'])
    #
    # def test_role_delete(self):
    #     role = role_factory.new_into_db(school_id=self.school.id)
    #     token = self.get_auth_token(self.user.username, self.user.raw_password)
    #
    #     response = self.client.delete(
    #         '/permissions/role/{}'.format(role.id),
    #         headers={'Authorization': 'JWT ' + token}
    #     )
    #
    #     self.assertEqual(response.status_code, 200)
    #
    #     role_from_db = Role.query.get(role.id)
    #     self.assertIsNone(role_from_db)
    #
    # def test_role_update_name(self):
    #     role = role_factory.new_into_db(school_id=self.school.id)
    #     new_name = 'New Name'
    #     self.assertNotEqual(role.name, new_name)
    #
    #     token = self.get_auth_token(self.user.username, self.user.raw_password)
    #
    #     response = self.client.put(
    #         '/permissions/role/{}'.format(role.id),
    #         data=json.dumps({'name': new_name}),
    #         headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
    #     )
    #
    #     self.assertEqual(response.status_code, 200)
    #
    #     role_from_db = Role.query.get(role.id)
    #     self.assertEqual(new_name, role_from_db.name)
    #
    # def test_role_update_permissions(self):
    #     permission = permission_factory.new_into_db(school_id=self.school.id)
    #     role = role_factory.new_into_db(school_id=self.school.id, permissions=[])
    #     self.assertEqual(role.permissions, [])
    #
    #     token = self.get_auth_token(self.user.username, self.user.raw_password)
    #
    #     response = self.client.put(
    #         '/permissions/role/{}'.format(role.id),
    #         data=json.dumps({'permissions': [permission.id]}),
    #         headers={'Content-Type': 'application/json', 'Authorization': 'JWT ' + token}
    #     )
    #
    #     self.assertEqual(response.status_code, 200)
    #
    #     role_from_db = Role.query.get(role.id)
    #     self.assertEqual(permission.id, role_from_db.permissions[0].id)
    #
    # def test_grant_role(self):
    #     user = user_factory.new_into_db(school_id=self.school.id)
    #     role = role_factory.new_into_db(school_id=self.school.id)
    #     self.assertFalse(user.has_roles({role.name}))
    #
    #     data_to_send = {
    #         'user_id': user.id,
    #         'role_id': role.id,
    #     }
    #
    #     token = self.get_auth_token(self.user.username, self.user.raw_password)
    #
    #     response = self.client.post(
    #         '/permissions/role/grant',
    #         data=json.dumps(data_to_send),
    #         headers={
    #             'Content-Type': 'application/json',
    #             'Authorization': 'JWT ' + token
    #         }
    #     )
    #
    #     self.assertEqual(response.status_code, 201)
    #     self.assertTrue(user.has_roles({role.name}))
    #
    # def test_remove_role(self):
    #     role = role_factory.new_into_db(school_id=self.school.id)
    #     user = user_factory.new_into_db(
    #         school_id=self.school.id, roles=[role.name])
    #
    #     self.assertTrue(user.has_roles({role.name}))
    #
    #     data_to_send = {
    #         'user_id': user.id,
    #         'role_id': role.id,
    #     }
    #
    #     token = self.get_auth_token(self.user.username, self.user.raw_password)
    #
    #     response = self.client.delete(
    #         '/permissions/role/grant',
    #         data=json.dumps(data_to_send),
    #         headers={
    #             'Content-Type': 'application/json',
    #             'Authorization': 'JWT ' + token
    #         }
    #     )
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertFalse(user.has_roles({role.name}))
