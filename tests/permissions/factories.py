from faker import Faker

from app import db

from app.permissions.models import Permission, Role

fake = Faker()


class PermissionFactory:

    def __init__(self):
        pass

    def new(self, **kwargs):

        school_id = fake.random_int()

        if 'school_id' in kwargs:
            school_id = kwargs['school_id']

        id = fake.random_int()
        permission = Permission(
            name=fake.first_name(),
            description=fake.text()[:200],
            school_id=school_id
        )
        permission.id = id
        return permission

    def new_into_db(self, **kwargs):
        permission = self.new(**kwargs)
        db.session.add(permission)

        db.session.commit()
        return permission


class RoleFactory:
    def __init__(self):
        pass

    def new(self, permission_names=[], **kwargs):
        school_id = fake.random_int()

        if 'school_id' in kwargs:
            school_id = kwargs['school_id']

        id = fake.random_int()
        role = Role(
            name=fake.first_name(),
            school_id=school_id
        )
        role.id = id

        for permission_name in permission_names:
            role.add_permission_by_name(permission_name)
        return role

    def new_into_db(self, **kwargs):
        role = self.new(**kwargs)
        db.session.add(role)

        db.session.commit()
        return role
