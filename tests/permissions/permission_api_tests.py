import json

from tests import APITestCase
from tests.school.factories import SchoolFactory
from tests.user.factories import UserFactory
from tests.permissions.factories import PermissionFactory

from app.user.models import User
from app.permissions.models import Permission, Role

school_factory = SchoolFactory()
user_factory = UserFactory()
permission_factory = PermissionFactory()


class PermissionAPITestCase(APITestCase):
    def setUp(self):
        super(PermissionAPITestCase, self).setUp()
        self.school = school_factory.new_into_db()
        self.user = user_factory.new_into_db(school_id=self.school.id, permissions=['Administrator'])

    def tearDown(self):
        super(PermissionAPITestCase, self).tearDown()

    # def test_set_defaults(self):
        # school = school_factory.new_into_db(without_roles=True, without_permissions=True)
        # user = user_factory.new_into_db(school_id=school.id)
        #
        # token = self.get_auth_token(user.username, user.raw_password)
        #
        # response = self.client.post(
        #     '/permissions/set-defaults',
        #     headers={'Authorization': 'JWT ' + token})
        #
        # json_response = json.loads(response.data.decode('utf-8'))
        # self.assertTrue(json_response['success'])
        #
        # permission_query = Permission.query.filter_by(school_id=school.id)
        # self.assertIsNotNone(permission_query.first())
        #
        # role_query = Role.query.filter_by(school_id=school.id)
        # self.assertIsNotNone(role_query.first())
        #
        # user_from_db = User.query.get(user.id)
        # self.assertIsNotNone(user_from_db)
        # role_names = [role.name for role in user_from_db.roles]
        # self.assertIn('ADMINISTRATOR', role_names)

    def test_permission_create(self):
        permission = permission_factory.new(school_id=self.school.id)

        # Assert permission does not already exist.
        permission_query = Permission.query.filter_by(
            name=permission.name, school_id=self.school.id)
        self.assertIsNone(permission_query.first())

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.post(
            '/permissions/permission',
            data=json.dumps(permission.to_dict()),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(permission_query.first())

    def test_permission_listing(self):
        permissions = [permission_factory.new_into_db(school_id=self.school.id)]

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.get(
            '/permissions/permission',
            headers={'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        for permission in permissions:
            self.assertIn(permission.to_dict(), json_response['permissions'])

    def test_permission_detail(self):
        permission = permission_factory.new_into_db(school_id=self.school.id)

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.get(
            '/permissions/permission/{}'.format(permission.id),
            headers={'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data.decode('utf-8'))

        self.assertEqual(permission.id, json_response['permission']['id'])

    def test_permission_delete(self):
        permission = permission_factory.new_into_db(school_id=self.school.id)

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.delete(
            '/permissions/permission/{}'.format(permission.id),
            headers={'Authorization': 'JWT ' + token}
        )

        self.assertEqual(response.status_code, 200)

        permission_from_db = Permission.query.get(permission.id)
        self.assertIsNone(permission_from_db)

    def test_permission_update_name(self):
        permission = permission_factory.new_into_db(school_id=self.school.id)
        new_name = 'New Name'
        self.assertNotEqual(permission.name, new_name)

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.put(
            '/permissions/permission/{}'.format(permission.id),
            data=json.dumps({'name': new_name}),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)

        permission_from_db = Permission.query.get(permission.id)

        self.assertIsNotNone(permission_from_db)
        self.assertEqual(permission_from_db.name, new_name)

    def test_permission_update_description(self):
        permission = permission_factory.new_into_db(school_id=self.school.id)
        new_description = 'Description which is new'
        self.assertNotEqual(permission.name, new_description)

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.put(
            '/permissions/permission/{}'.format(permission.id),
            data=json.dumps({'description': new_description}),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)

        permission_from_db = Permission.query.get(permission.id)

        self.assertIsNotNone(permission_from_db)
        self.assertEqual(permission_from_db.description, new_description)

    def test_grant_permission(self):
        user = user_factory.new_into_db(school_id=self.school.id)
        permission = permission_factory.new_into_db(school_id=self.school.id)
        self.assertNotIn(permission.id, [p.id for p in user.permissions])

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.post(
            '/permissions/permission/grant'.format(permission.id),
            data=json.dumps({'user_id': user.id, 'permission_id': permission.id}),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 201)

        # Do not need to fetch a new user object as permissions runs it's own query
        self.assertIn(permission.id, [p.id for p in user.permissions])

    def test_revoke_permission(self):
        permission = permission_factory.new_into_db(school_id=self.school.id)
        user = user_factory.new_into_db(school_id=self.school.id, permissions=[permission.name])
        self.assertIn(permission.id, [p.id for p in user.permissions])

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.delete(
            '/permissions/permission/grant'.format(permission.id),
            data=json.dumps({'user_id': user.id, 'permission_id': permission.id}),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)
        # Do not need to fetch a new user object as permissions runs it's own query
        self.assertNotIn(permission.id, [p.id for p in user.permissions])

    def test_revoke_permission_all(self):
        permission = permission_factory.new_into_db(school_id=self.school.id)
        user = user_factory.new_into_db(school_id=self.school.id, permissions=[permission.name])
        self.assertIn(permission.id, [p.id for p in user.permissions])

        token = self.get_auth_token(self.user.username, self.user.raw_password)

        response = self.client.delete(
            '/permissions/permission/grant'.format(permission.id),
            data=json.dumps({'user_id': user.id, 'all': True}),
            headers={'Authorization': 'JWT ' + token, 'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 200)
        # Do not need to fetch a new user object as permissions runs it's own query
        self.assertEqual(0, len(user.permissions))
