from app import db
from app.exceptions import FieldInUseError
from app.helper import get_record_by_id, json_from_request, check_keys
from app.user.models import Form
from flask import g, jsonify


def create_form(request):
    expected_keys = ["name"]
    data = json_from_request(request)
    check_keys(expected_keys, data)

    #  Validate name
    if Form.query.filter_by(name=data['name']).first() is not None:
        raise FieldInUseError("name")

    form = Form(name=data['name'], school_id=g.user.school_id)
    db.session.add(form)
    db.session.commit()
    return jsonify({'success': True, 'form': form.to_dict()}), 201


def list_forms(request):
    forms = Form.query.filter_by(school_id=g.user.school_id).all()
    form_list = [f.to_dict() for f in forms]
    return jsonify({'success': True, 'forms': form_list})


def edit_form(request, form_id):
    data = json_from_request(request)
    form = get_record_by_id(form_id, Form)

    if "name" in data.keys():
        # Validate name
        if Form.query.filter_by(name=data['name']).first() is not None:
            raise FieldInUseError("name")
        form.name = data['name']

    db.session.add(form)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Updated.'})


def form_detail(request, form_id):
    form = get_record_by_id(form_id, Form)
    return jsonify({'success': True, 'form': form.to_dict()})


def delete_form(request, form_id):
    form = get_record_by_id(form_id, Form)
    db.session.delete(form)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Deleted.'})
