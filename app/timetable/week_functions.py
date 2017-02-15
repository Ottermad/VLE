from app import db
from app.helper import check_keys, json_from_request
from app.timetable.models import Week
from flask import g, jsonify


def create_week(request):
    expected_keys = [
        'name'
    ]
    json_data = json_from_request(request)
    check_keys(expected_keys, json_data)

    week = Week(
        name=json_data['name'],
        school_id=g.user.school_id
    )

    db.session.add(week)
    db.session.commit()

    return jsonify(week.to_dict()), 201
