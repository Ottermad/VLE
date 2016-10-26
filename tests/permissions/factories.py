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
