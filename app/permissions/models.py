from app import db

role_permissions = db.Table(
    'role_permissions',
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

user_permissions = db.Table(
    'user_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
)

user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class Permission(db.Model):
    """Model representing a permission a user can have."""
    __table_args__ = (
        db.UniqueConstraint('school_id', 'name'),
        {}
    )

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    name = db.Column(db.String(120))
    description = db.Column(db.String(240))

    # Provides the default permissions to create
    DEFAULTS = [
        {
            "name": "Administrator",
            "description": "Allows a user to be an admin."
        },
        {
            "name": "Teacher",
            "description": "Allows a user to be a teacher."
        },
        {
            "name": "Student",
            "description": "Allows a user to be a student."
        },
        {
            "name": "Parent",
            "description": "Allows user to be a parent."
        },
        # {
        #     "name": "CRUD_USERS",
        #     "description": "Allows a user to create, read, update and delete users."
        # },
        # {
        #     "name": "CRUD_PERMISSIONS",
        #     "description": "Allows a user to create, read, update and delete permissions."
        # }
    ]

    def __init__(self, name, school_id, description):
        self.name = name
        self.school_id = school_id
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'name': self.name,
            'description': self.description
        }

    @classmethod
    def default_permissions(cls, school_id):
        permissions = []
        for permission in cls.DEFAULTS:
            permissions.append(cls(school_id=school_id, **permission))
        return permissions


class Role(db.Model):
    """
    Model representing a role which a user can have

    Used to grant permissions as a group.
    """

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    name = db.Column(db.String(120))
    permissions = db.relationship(
        'Permission', secondary=role_permissions,
        backref=db.backref('role_permissions', lazy='dynamic')
    )

    DEFAULT_ROLES = {
        'ADMINISTRATOR': ['CRUD_USERS', 'CRUD_PERMISSIONS']
    }

    def __init__(self, name, school_id):
        self.name = name
        self.school_id = school_id

    def __str__(self):
        return "{}: {}".format(self.school_id, self.name)

    def __repr__(self):
        return self.__str__()

    def add_permission_by_name(self, name):
        """Add permissions to role but not commit to database."""
        permission = Permission.query.filter_by(school_id=self.school_id, name=name).first()
        if permission is None:
            raise Exception
        self.permissions.append(permission)

    def to_dict(self, nest_permissions=False):
        dictionary = {
            'id': self.id,
            'school_id': self.school_id,
            'name': self.name,
        }
        if nest_permissions:
            dictionary['permissions'] = [p.to_dict() for p in self.permissions]
        return dictionary

    @classmethod
    def default_roles(cls, school_id):
        roles =[]
        for name, permissions in cls.DEFAULT_ROLES.items():
            role = Role(name=name, school_id=school_id)
            for permission in permissions:
                role.add_permission_by_name(permission)
            roles.append(role)
        return roles

