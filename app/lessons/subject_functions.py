from flask import g, jsonify

from app import db
from app.exceptions import FieldInUseError, NotFoundError, UnauthorizedError
from app.helper import json_from_request, check_keys
from app.lessons.models import Subject


def create_subject(name, school_id):
    # Check name does not already exist for school
    if Subject.query.filter_by(name=name, school_id=school_id).first() is not None:
        raise FieldInUseError()

    subject = Subject(name=name, school_id=school_id)
    db.session.add(subject)
    db.session.commit()
    return subject


def create_subject_view(request):
    data = json_from_request(request)
    expected_keys = ["name"]
    check_keys(expected_keys, data)

    subject = create_subject(data['name'], g.user.school_id)

    return jsonify({'success': True, 'subject': subject.to_dict()}), 201


def subjects_for_school(school_id):
    return Subject.query.filter_by(school_id=school_id).all()


def list_subject_view(request):
    # Get subjects and convert to dicts
    subjects = [s.to_dict() for s in subjects_for_school(g.user.school_id)]
    return jsonify({'success': True, 'subjects': subjects})


def subject_detail_view(request, subject_id):
    subject = get_subject_by_id(subject_id)
    return jsonify({'success': True, 'subject': subject.to_dict()})


def subject_delete_view(request, subject_id):
    subject = get_subject_by_id(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Deleted'})


def get_subject_by_id(subject_id, custom_not_found_error=None):
    # Check user specified is in the correct school
    subject = Subject.query.filter_by(id=subject_id).first()
    if subject is None:
        if custom_not_found_error:
            raise custom_not_found_error

        raise NotFoundError()
    if subject.school_id != g.user.school_id:
        raise UnauthorizedError()

    return subject
