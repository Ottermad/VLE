from flask import Blueprint, jsonify, g, request
from flask_jwt import jwt_required

from .decorators import permissions_required

from app.permissions.permission_functions import set_default_permissions, permission_create, permissions_list, \
    permission_detail, permission_delete, permission_update, grant_permission, remove_permission
from app.permissions.role_functions import (
    grant_role,
    remove_role,
    role_create,
    role_listing,
    role_detail,
    role_delete,
    role_update
)

permissions_blueprint = Blueprint('permissions', __name__, url_prefix='/permissions')


@permissions_blueprint.route('/set-defaults', methods=["POST"])
@jwt_required()
def set_defaults_view():
    return set_default_permissions(request)


@permissions_blueprint.route('/permission', methods=["POST", "GET"])
@jwt_required()
@permissions_required({'Administrator'})
def permission_listing_or_create_view():
    """Return a list of all permissions for a school or create a new one."""
    if request.method == "POST":
        return permission_create(request)
    else:
        return permissions_list(request)


@permissions_blueprint.route('/permission/<int:permission_id>', methods=["GET", "PUT", "DELETE"])
@jwt_required()
@permissions_required({'Administrator'})
def permission_detail_view(permission_id):
    if request.method == "GET":
        return permission_detail(request, permission_id)
    if request.method == "DELETE":
        return permission_delete(request, permission_id)
    if request.method == "PUT":
        return permission_update(request, permission_id)


@permissions_blueprint.route('/permission/grant', methods=["POST", "DELETE"])
@jwt_required()
@permissions_required({'Administrator'})
def grant_or_remove_permission_view():
    """Grant a permission to a user."""
    if request.method == "POST":
        return grant_permission(request)
    elif request.method == "DELETE":
        return remove_permission(request)


@permissions_blueprint.route('/role', methods=["POST", "GET"])
@jwt_required()
@permissions_required({'Administrator'})
def role_listing_or_create_view():
    """Return a list of all roles for a school or create a new one."""
    if request.method == "POST":
        return role_create(request)
    else:
        return role_listing(request)


@permissions_blueprint.route('/role/<int:role_id>', methods=["GET", "PUT", "DELETE"])
@jwt_required()
@permissions_required({'Administrator'})
def role_detail_view(role_id):
    if request.method == "GET":
        return role_detail(request, role_id)
    if request.method == "DELETE":
        return role_delete(request, role_id)
    if request.method == "PUT":
        return role_update(request, role_id)


@permissions_blueprint.route('/role/grant', methods=["POST", "DELETE"])
@jwt_required()
@permissions_required({'Administrator'})
def grant_or_remove_role_view():
    """Grant a role to a user or remove a role from a user."""
    if request.method == "POST":
        return grant_role(request)
    elif request.method == "DELETE":
        return remove_role(request)
