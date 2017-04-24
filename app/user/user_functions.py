from app import db
from app.exceptions import FieldInUseError
from app.helper import get_boolean_query_param, json_from_request, check_keys, get_record_by_id
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

    if User.query.filter_by(email=data['email']).first() is not None:
        raise FieldInUseError("email")

    if User.query.filter_by(username=data['username'], school_id=g.user.school_id).first() is not None:
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


def user_update(request, user_id):
    data = json_from_request(request)
    user = get_record_by_id(user_id, User)

    possible_keys = ["first_name", "last_name", "password", "username", "email"]

    for key in possible_keys:
        if key in data.keys():
            if key == 'password':
                user.__setattr__(key, User.generate_password_hash(data[key]))
            else:
                user.__setattr__(key, data[key])

    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Updated.'})


def user_delete(request, user_id):
    user = get_record_by_id(user_id, User)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Deleted.'})


def user_detail(request, user_id):
    user = get_record_by_id(user_id, User)
    nest_roles = get_boolean_query_param(request, 'nest-roles')
    nest_role_permissions = get_boolean_query_param(request, 'nest-role-permissions')
    nest_permissions = get_boolean_query_param(request, 'nest-permissions')
    return jsonify({
        'success': True,
        "user": user.to_dict(
            nest_roles=nest_roles,
            nest_role_permissions=nest_role_permissions,
            nest_permissions=nest_permissions
        )
    })


def current_user_details(request):
    nest_roles = get_boolean_query_param(request, 'nest-roles')
    nest_role_permissions = get_boolean_query_param(request, 'nest-role-permissions')
    nest_permissions = get_boolean_query_param(request, 'nest-permissions')
    user_dict = g.user.to_dict(
        nest_roles=nest_roles,
        nest_role_permissions=nest_role_permissions,
        nest_permissions=nest_permissions
    )
    return jsonify({'success': True, 'user': user_dict})
