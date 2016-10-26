from faker import Faker

from app import db

from app.school.models import School
from app.permissions.models import Permission, Role

fake = Faker()


class SchoolFactory:

    def __init__(self):
        pass

    def new(self):
        id = fake.random_int()
        school = School(
            school_name="school{}".format(id)
        )
        school.id = fake.random_int()
        return school

    def new_into_db(self):
        school = self.new()
        db.session.add(school)

        # Create permissions

        for permission in Permission.default_permissions(school.id):
            db.session.add(permission)

        # Create roles
        for role in Role.default_roles(school.id):
            db.session.add(role)

        db.session.commit()
        return school
