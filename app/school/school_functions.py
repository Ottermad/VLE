from flask import jsonify

from app import db
from app.exceptions import FieldInUseError
from app.helper import json_from_request, check_keys

from .models import School


def create_school(request):
    data = json_from_request(request)

    expected_keys = ["name"]
    check_keys(expected_keys, data)

    if School.query.filter_by(name=data['name']).first() is not None:
        raise FieldInUseError("name")

    school = School(school_name=data['name'])

    db.session.add(school)
    db.session.commit()

    return jsonify({'success': True, 'school': school.to_dict()}), 201
