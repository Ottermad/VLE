from faker import Faker

from tests.school.factories import SchoolFactory

from app import db
from app.user.models import User
from app.permissions.models import Permission

fake = Faker()

school_factory = SchoolFactory()


class UserFactory:
    def __init__(self):
        self.school = school_factory.new()

    def new(self, school_id=None, permissions=[]):
        if school_id is None:
            school_id = self.school.id

        password = fake.password()

        user = User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            password=password,
            school_id=school_id,
            username=fake.user_name()
        )
        user.raw_password = password

        permission_query = Permission.query.filter(Permission.name.in_(permissions), Permission.school_id == school_id)
        [user.permissions.append(p) for p in permission_query]
        return user

    def new_into_db(self, **kwargs):
        user = self.new(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user




