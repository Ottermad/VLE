from app import db
from app.exceptions import FieldInUseError
from app.helper import get_boolean_query_param, json_from_request, check_keys
from flask import jsonify, g
from .models import User


def user_listing(request):
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


def user_create(request):
    #  Decode the JSON data
    data = json_from_request(request)

    # Validate data
    expected_keys = ["first_name", "last_name", "password", "username", "email"]
    check_keys(expected_keys, data)

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
        school_id=g.user.school_id
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True, "user": user.to_dict()}), 201


