from flask import Blueprint, request, jsonify

from app.exceptions import FieldInUseError, MissingKeyError, NoJSONError
from app.helper import check_keys, json_from_request

from .models import School, db

school_blueprint = Blueprint("school", __name__, url_prefix="/school")


@school_blueprint.route("/")
def index():
    return "School Index"


@school_blueprint.route("/school", methods=["POST"])
def create():
    data = json_from_request(request)

    expected_keys = ["name"]
    check_keys(expected_keys, data)

    if School.query.filter_by(name=data['name']).first() is not None:
        raise FieldInUseError("name")

    school = School(school_name=data['name'])
    db.session.add(school)
    db.session.commit()

    return jsonify({'success': True, 'school': school.to_dict()}), 201
