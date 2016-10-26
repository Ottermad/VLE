from functools import wraps

from flask import abort, g

from app.exceptions import CustomError


def permissions_required(permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user.has_permissions(permissions):
                return f(*args, **kwargs)

            raise CustomError(403)
        return decorated_function
    return decorator
