from app.exceptions import BlankValueError
from .exceptions import NoJSONError, MissingKeyError, NotFoundError, UnauthorizedError
from flask import g


def json_from_request(request):
    data = request.get_json()
    if data is None:
        raise NoJSONError()
    return data


def check_keys(expected_keys, data):
    for key in expected_keys:
        if key not in data.keys():
            raise MissingKeyError(key)


def get_boolean_query_param(request, param_name):
    param = request.args.get(param_name)
    if param is not None:
         return param.lower() == "true"
    return False


def get_record_by_id(model_id, model, custom_not_found_error=None, check_school_id=True):
    # Check user specified is in the correct school
    record = model.query.filter_by(id=model_id).first()
    if record is None:
        if custom_not_found_error:
            raise custom_not_found_error

        raise NotFoundError()
    if check_school_id:
        if record.school_id != g.user.school_id:
            raise UnauthorizedError()

    return record


def check_values_not_blank(keys, data):
    for key in keys:
        if isinstance(data[key], str):
            value = data[key].strip()
            if value is None or value == '':
                raise BlankValueError(key)
