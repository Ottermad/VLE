from flask import jsonify

from app import db
from app.exceptions import FieldInUseError, CustomError
from app.helper import json_from_request, check_keys, check_values_not_blank

from .models import School
from app.permissions.models import Permission
from app.user.models import User


def create_school(request):
    # This may not longer be needed and should be removed
    data = json_from_request(request)

    expected_keys = ["name"]
    check_keys(expected_keys, data)

    if School.query.filter_by(name=data['name']).first() is not None:
        raise FieldInUseError("name")

    school = School(school_name=data['name'])

    db.session.add(school)
    db.session.commit()

    return jsonify({'success': True, 'school': school.to_dict()}), 201


def signup_school(request):
    # Fetch JSON data from request
    data = json_from_request(request)

    # List of keys we expect to see in JSON
    expected_keys = ["school_name", "first_name", "last_name", "password", "username", "email"]

    # Checks keys are present in JSON and throws error if not which is automatically caught and converted into a error message
    check_keys(expected_keys, data)

    # Checks values for keys are not blank
    check_values_not_blank(expected_keys, data)

    # Create school object with user's data
    school = School(school_name=data['school_name'])

    # Add school to db
    db.session.add(school)
    db.session.commit()

    # Create user
    # Check email not already in use
    if User.query.filter_by(email=data['email']).first() is not None:
        raise FieldInUseError("email")

    # Check username is not already in use
    if User.query.filter_by(username=data['username']).first() is not None:
        raise FieldInUseError("username")

    # Create user
    user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=data['password'],
        username=data['username'],
        school_id=school.id
    )

    # Add user to db
    db.session.add(user)
    db.session.commit()

    # Create permissions
    for permission in Permission.default_permissions(school.id):
        db.session.add(permission)
    db.session.commit()

    #  Assign user to admin permissions
    permission = Permission.query.filter_by(name="Administrator", school_id=school.id).first()
    user.permissions.append(permission)
    db.session.add(user)
    db.session.commit()

    # Return success message as JSON
    return jsonify({'success': True})
