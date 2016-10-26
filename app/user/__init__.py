from flask import Blueprint, request, jsonify, g
from flask_jwt import jwt_required

from app.exceptions import FieldInUseError, CustomError
from app.helper import json_from_request, check_keys, get_boolean_query_param
from app.permissions.decorators import permissions_required
from app.school.models import School

from .models import db, User

user_blueprint = Blueprint("user", __name__, url_prefix="/user")


@user_blueprint.route("/")
def index():
    return "User Index"


@user_blueprint.route("/user", methods=["GET", "POST"])
@jwt_required()
@permissions_required({'CRUD_USERS'})
def create_user():
    """Route to create User from a POST request."""
    if request.method == "GET":
        nest_roles = get_boolean_query_param(request, 'nest-roles')
        nest_role_permissions = get_boolean_query_param(request, 'nest-role-permissions')
        nest_permissions = get_boolean_query_param(request, 'nest-permissions')

        users = User.query.filter_by(school_id=g.user.school_id)
        users_list = [
            u.to_dict(
                nest_roles=nest_roles,
                nest_role_permissions=nest_role_permissions,
                nest_permissions=nest_permissions
            ) for u in users
        ]
        return jsonify({'success': True, 'users': users_list})

    if request.method == "POST":
        # Decode the JSON data
        data = json_from_request(request)

        # Validate data
        expected_keys = ["first_name", "last_name", "password", "username", "email", "school_id"]
        check_keys(expected_keys, data)

        if School.query.filter_by(id=data['school_id']).first() is None:
            raise CustomError(401, message="School with id: {} does not exist.".format(data['school_id']))

        if User.query.filter_by(email=data['email']).first() is not None:
            raise FieldInUseError("email")

        if User.query.filter_by(username=data['username'], school_id=data['school_id']).first() is not None:
            raise FieldInUseError("username")

        # Create user
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            username=data['username'],
            school_id=data['school_id']
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({"success": True, "user": user.to_dict()}), 201
