from flask import Blueprint, jsonify, g, request
from flask_jwt import jwt_required

from app.exceptions import CustomError, UnauthorizedError, FieldInUseError, NotFoundError
from app.helper import check_keys, json_from_request

from .models import Permission, Role, role_permissions, db
from .decorators import permissions_required

from app.user.models import User

permissions_blueprint = Blueprint('permissions', __name__, url_prefix='/permissions')


@permissions_blueprint.route('/set-defaults/', methods=["POST"])
@jwt_required()
def default():
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

    # Assign user to admin role
    role = Role.query.filter_by(name="ADMINISTRATOR", school_id=school_id).first()
    g.user.roles.append(role)
    db.session.add(g.user)
    db.session.commit()

    # Return success status
    return jsonify({'success': True}), 201


@permissions_blueprint.route('/permission', methods=["POST", "GET"])
@jwt_required()
@permissions_required({'CRUD_PERMISSIONS'})
def permission_listing():
    """Return a list of all permissions for a school or create a new one."""
    if request.method == "POST":
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

    else:
        permissions = Permission.query.filter_by(school_id=g.user.school_id)
        return jsonify({
            'permissions': [p.to_dict() for p in permissions]
        }), 200


@permissions_blueprint.route('/permission/<int:permission_id>', methods=["GET", "PUT", "DELETE"])
@jwt_required()
@permissions_required({'CRUD_PERMISSIONS'})
def permission_detail(permission_id):
    # Check permission exists
    permission = Permission.query.filter_by(id=permission_id).first()

    if permission is None:
        raise NotFoundError()

    # Check permission in correct school
    if permission.school_id != g.user.school_id:
        raise UnauthorizedError()

    # Check request method
    if request.method == "GET":
        return jsonify({'success': True, 'permission': permission.to_dict()})
    if request.method == "DELETE":
        db.session.delete(permission)
        message = "Deleted."
    if request.method == "PUT":
        data = json_from_request(request)
        if "name" in data.keys():
            permission.name = data['name']
        if "description" in data.keys():
            permission.description = data['description']
        message = "Updated."

    db.session.commit()

    # Return
    return jsonify({'success': True, "message": message})


@permissions_blueprint.route('/permission/grant', methods=["POST"])
@jwt_required()
@permissions_required({'CRUD_PERMISSIONS'})
def grant_permission():
    """Grant a permission to a user."""
    data = json_from_request(request)

    expected_keys = ["user_id", "permission_id"]
    check_keys(expected_keys, data)

    # Check user specified is in the correct school
    user = User.query.filter_by(id=data['user_id']).first()
    if user is None:
        raise CustomError(409, message="Invalid user_id.")
    if user.school_id != g.user.school_id:
        raise UnauthorizedError()

    # Check the permission specified is in the correct school
    permission = Permission.query.filter_by(id=data['permission_id']).first()
    if permission is None:
        raise CustomError(409, message="Invalid permission_id.")
    if permission.school_id != g.user.school_id:
        raise UnauthorizedError()

    # Check user does not have the permission
    for p in user.permissions:
        if p.id == data['permission_id']:
            raise CustomError(409, message="User with id: {} already has permission with id: {}".format(
                data['user_id'], data['permission_id']))

    user.permissions.append(permission)
    db.session.add(user)
    db.session.commit()

    # Return success status
    return jsonify({'success': True}), 201
