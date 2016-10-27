from flask import g, jsonify

from app import CustomError, db
from app.exceptions import FieldInUseError, NotFoundError, UnauthorizedError
from app.helper import json_from_request, check_keys
from app.user.user_functions import get_user_by_id

from .models import Permission, Role


def set_default_permissions(request):
    """
    Create default roles and permissions for school.

    Uses the currently logged in user as the initial admin.
    Only works if permissions do not exist yet.
    """

    school_id = g.user.school_id

    # Check permissions not created yet.
    if Permission.query.filter_by(school_id=school_id).first() is not None:
        raise CustomError(401, message='Permissions already setup.')

    # Create permissions
    for permission in Permission.default_permissions(school_id):
        db.session.add(permission)
    db.session.commit()

    # Create roles
    for role in Role.default_roles(school_id):
        db.session.add(role)
    db.session.commit()

    #  Assign user to admin role
    role = Role.query.filter_by(name="ADMINISTRATOR", school_id=school_id).first()
    g.user.roles.append(role)
    db.session.add(g.user)
    db.session.commit()

    # Return success status
    return jsonify({'success': True}), 201


def permission_create(request):
    """Create a Permission from a POST request."""
    data = json_from_request(request)
    expected_keys = ["name", "description"]
    check_keys(expected_keys, data)

    # Check name not in use by school
    if Permission.query.filter_by(name=data['name'], school_id=g.user.school_id).first() is not None:
        raise FieldInUseError("name")

    permission = Permission(name=data['name'], description=data['description'], school_id=g.user.school_id)
    db.session.add(permission)
    db.session.commit()

    return jsonify({'success': True, 'permission': permission.to_dict()}), 201


def permissions_list(request):
    """Returns a list of permissions."""
    permissions = Permission.query.filter_by(school_id=g.user.school_id)
    return jsonify({
        'permissions': [p.to_dict() for p in permissions]
    }), 200


def permission_detail(request, permission_id):
    permission = get_permission_by_id(permission_id)
    return jsonify({'success': True, 'permission': permission.to_dict()})


def permission_delete(request, permission_id):
    permission = get_permission_by_id(permission_id)
    db.session.delete(permission)
    db.session.commit()
    return jsonify({'success': True, "message": "Deleted."})


def permission_update(request, permission_id):
    permission = get_permission_by_id(permission_id)
    data = json_from_request(request)
    if "name" in data.keys():
        permission.name = data['name']
    if "description" in data.keys():
        permission.description = data['description']
    db.session.add(permission)
    db.session.commit()

    return jsonify({'success': True, "message": "Updated."})


def grant_permission(request):
    data = json_from_request(request)

    expected_keys = ["user_id", "permission_id"]
    check_keys(expected_keys, data)

    # Check user specified is in the correct school
    user = get_user_by_id(data['user_id'], CustomError(409, message="Invalid user_id."))

    #  Check the permission specified is in the correct school
    permission = get_permission_by_id(data['permission_id'], CustomError(409, message="Invalid permission_id."))

    # Check user does not have the permission
    for p in user.permissions:
        if p.id == data['permission_id']:
            raise CustomError(409, message="User with id: {} already has permission with id: {}".format(
                data['user_id'], data['permission_id']))

    user.permissions.append(permission)
    db.session.add(user)
    db.session.commit()

    # Return success status
    return jsonify({'success': True}), 201


def remove_permission(request):
    data = json_from_request(request)

    expected_keys = ["user_id", "permission_id"]
    check_keys(expected_keys, data)

    # Check user specified is in the correct school
    user = get_user_by_id(data['user_id'], CustomError(409, message="Invalid user_id."))

    #  Check the permission specified is in the correct school
    permission = get_permission_by_id(data['permission_id'], CustomError(409, message="Invalid permission_id."))

    #  Check the user has the role
    if permission.id not in [p.id for p in user.permissions]:
        raise CustomError(
            409,
            message="User with id: {} does not have permission with id: {}".format(data['user_id'],
                                                                                   data['permission_id'])
        )

    user.permissions.remove(permission)

    db.session.add(user)
    db.session.commit()

    # Return success status
    return jsonify({'success': True}), 200


def get_permission_by_id(permission_id, custom_not_found_error=None):
    # Check permission exists
    permission = Permission.query.filter_by(id=permission_id).first()

    if permission is None:
        if custom_not_found_error is not None:
            raise custom_not_found_error

        raise NotFoundError()

    #  Check permission in correct school
    if permission.school_id != g.user.school_id:
        raise UnauthorizedError()
    return permission