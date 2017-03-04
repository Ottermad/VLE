from faker import Faker

from app import db

from app.school.models import School
from app.permissions.models import Permission, Role

fake = Faker()


class SchoolFactory:

    def __init__(self):
        pass

    def new(self, **kwargs):
        id = fake.random_int()
        school = School(
            school_name="school{}".format(id)
        )
        school.id = id
        return school

    def new_into_db(self, without_roles=False, without_permissions=False, **kwargs):
        school = self.new(**kwargs)
        db.session.add(school)

        # Create permissions
        if not without_permissions:
            for permission in Permission.default_permissions(school.id):
                db.session.add(permission)

        # Create roles
        # if not without_roles:
        #     for role in Role.default_roles(school.id):
        #         db.session.add(role)

        db.session.commit()
        return school
