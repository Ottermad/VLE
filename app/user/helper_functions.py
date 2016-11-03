from app.exceptions import NotFoundError, UnauthorizedError
from app.user.models import User
from flask import g


def get_user_by_id(user_id, custom_not_found_error=None):
    # Check user specified is in the correct school
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        if custom_not_found_error:
            raise custom_not_found_error

        raise NotFoundError()
    if user.school_id != g.user.school_id:
        raise UnauthorizedError()

    return user