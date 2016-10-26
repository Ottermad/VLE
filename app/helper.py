from .exceptions import NoJSONError, MissingKeyError


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
