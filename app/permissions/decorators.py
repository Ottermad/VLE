from functools import wraps

from flask import abort, g

from app.exceptions import CustomError

def permissions_required(permissions):

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_permissions = {permission.name for permission in g.user.permissions}
            if permissions.issubset(user_permissions):
                return f(*args, **kwargs)

            user_roles = set()
            for role in g.user.roles:
                for permission in role.permissions:
                    user_roles.add(permission.name)
            if permissions.issubset(user_roles):
                return f(*args, **kwargs)

            raise CustomError(403)
        return decorated_function
    return decorator