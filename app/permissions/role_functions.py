from flask import jsonify, g

from app import CustomError, db
from app.exceptions import FieldInUseError, NotFoundError, UnauthorizedError
from app.helper import json_from_request, check_keys
from app.user.user_functions import get_user_by_id

from .models import Role, Permission


def grant_role(request):
    data = json_from_request(request)

    expected_keys = ["user_id", "role_id"]
    check_keys(expected_keys, data)

    user = get_user_by_id(data['user_id'], custom_not_found_error=CustomError(409, message="Invalid user_id"))

    role = get_role_by_id(data['role_id'], custom_not_found_error=CustomError(409, message="Invalid role_id"))

    # Check that the user does not have the permission
    for inner_role in user.roles:
        if inner_role.id == data['role_id']:
            raise CustomError(409, message="User with id: {} already has role with id: {}".format(
                data['user_id'], data['role_id']))

    user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    # Return success status
    return jsonify({'success': True}), 201


def remove_role(request):
    data = json_from_request(request)

    expected_keys = ["user_id", "role_id"]
    check_keys(expected_keys, data)

    user = get_user_by_id(data['user_id'], custom_not_found_error=CustomError(409, message="Invalid user_id."))

    role = get_role_by_id(data['role_id'], custom_not_found_error=CustomError(409, message="Invalid role_id."))

    #  Check the user has the role
    if data['role_id'] not in [r.id for r in user.roles]:
        raise CustomError(
            409,
            message="User with id: {} does not have role with id: {}".format(data['user_id'], data['role_id'])
        )

    user.roles.remove(role)

    db.session.add(user)
    db.session.commit()

    # Return success status
    return jsonify({'success': True}), 201


def role_create(request):
    # Create a new role
    data = json_from_request(request)

    expected_keys = ["name", "permissions"]
    check_keys(expected_keys, data)

    #  Check name not in use
    if Role.query.filter_by(name=data['name'], school_id=g.user.school_id).first() is not None:
        raise FieldInUseError("name")

    # Check all permissions are valid
    permissions = Permission.query.filter(
        Permission.id.in_(data['permissions']),
        Permission.school_id == g.user.school_id
    )

    if permissions.count() != len(data['permissions']):
        raise CustomError(409, message="Invalid Permission.")

    role = Role(name=data['name'], school_id=g.user.school_id)
    [role.permissions.append(p) for p in permissions]
    db.session.add(role)
    db.session.commit()

    return jsonify({
        'success': True,
        'role': role.to_dict()
    }), 201


def role_listing(request):
    #  Return a listing of all roles
    roles = Role.query.filter_by(school_id=g.user.school_id)
    return jsonify({
        'success': True,
        'roles': [r.to_dict(nest_permissions=True) for r in roles]
    })


def role_detail(request, role_id):
    role = get_role_by_id(role_id)
    return jsonify({'success': True, 'role': role.to_dict()})


def role_delete(request, role_id):
    role = get_role_by_id(role_id)
    db.session.delete(role)
    db.session.commit()
    return jsonify({'success': True, "message": "Deleted."})


def role_update(request, role_id):
    role = get_role_by_id(role_id)
    data = json_from_request(request)
    if "name" in data.keys():
        role.name = data['name']
    if "permissions" in data.keys():
        # Check all permissions are valid
        permissions = Permission.query.filter(
            Permission.id.in_(data['permissions']),
            Permission.school_id == g.user.school_id
        )

        if permissions.count() != len(data['permissions']):
            raise CustomError(409, message="Invalid Permission.")

        role.permissions = [p for p in permissions]

    db.session.add(role)
    db.session.commit()
    return jsonify({'success': True, "message": "Updated."})


def get_role_by_id(role_id, custom_not_found_error=None):
    #  Check the role specified is in the correct school
    role = Role.query.filter_by(id=role_id).first()
    if role is None:
        if custom_not_found_error:
            raise custom_not_found_error

        raise NotFoundError()

    if role.school_id != g.user.school_id:
        raise UnauthorizedError()
    return role
