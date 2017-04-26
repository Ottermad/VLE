from app import db
from app.exceptions import FieldInUseError, CustomError
from app.helper import get_boolean_query_param, json_from_request, check_keys, get_record_by_id, check_values_not_blank
from app.user.models import Form
from flask import jsonify, g
from .models import User


def user_listing(request):
    nest_roles = get_boolean_query_param(request, 'nest-roles')
    nest_role_permissions = get_boolean_query_param(request, 'nest-role-permissions')
    nest_permissions = get_boolean_query_param(request, 'nest-permissions')
    nest_forms = get_boolean_query_param(request, 'nest-forms')

    users = User.query.filter_by(school_id=g.user.school_id)
    users_list = [
        u.to_dict(
            nest_roles=nest_roles,
            nest_role_permissions=nest_role_permissions,
            nest_permissions=nest_permissions,
            nest_form=nest_forms
        ) for u in users
        ]
    return jsonify({'success': True, 'users': users_list})


def user_create(request):
    #  Decode the JSON data
    data = json_from_request(request)

    # Validate data
    expected_keys = ["first_name", "last_name", "password", "username", "email"]
    check_keys(expected_keys, data)
    check_values_not_blank(expected_keys, data)

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

    if "form_id" in data.keys():
        # Validate form id
        form = get_record_by_id(data["form_id"], Form, custom_not_found_error=CustomError(409, message="Invalid form_id."))
        user.form_id = form.id

    db.session.add(user)
    db.session.commit()

    return jsonify({"success": True, "user": user.to_dict()}), 201


def user_update(request, user_id):
    data = json_from_request(request)
    user = get_record_by_id(user_id, User)

    possible_keys = ["first_name", "last_name", "password", "username", "email", "form_id"]
    check_values_not_blank(data.keys(), data)

    if "first_name" in data.keys():
        user.first_name = data['first_name']

    if "last_name" in data.keys():
        user.first_name = data['first_name']

    if "password" in data.keys():
        user.password = user.generate_password_hash(data['password'])

    if "email" in data.keys():
        if User.query.filter_by(email=data['email']).first() is not None:
            raise FieldInUseError("email")
        user.email = data['email']

    if "username" in data.keys():
        if User.query.filter_by(username=data['username'], school_id=g.user.school_id).first() is not None:
            raise FieldInUseError("username")
        user.username = data['username']

    if "form_id" in data.keys():
        # Validate form id
        form = get_record_by_id(data["form_id"], Form,
                                custom_not_found_error=CustomError(409, message="Invalid form_id."))
        user.form_id = form.id

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
