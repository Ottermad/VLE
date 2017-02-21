class CustomError(Exception):
    """Custom Error that contains a status code and can be easily converted to json."""
    def __init__(self, status_code, **kwargs):
        self.status_code = status_code
        self.kwargs = kwargs

    def to_dict(self):
        return {'status_code': self.status_code, 'error': True, **self.kwargs}


class MissingKeyError(CustomError):
    """Error for when a request is missing a key."""
    def __init__(self, key):
        super().__init__(409, message="Missing key: {}".format(key))


class BlankValueError(CustomError):
    """Error for when the value of a key is blank."""
    def __init__(self, key):
        super().__init__(409, message="Value for key: {} cannot be blank".format(key))


class NoJSONError(CustomError):
    """Error for when no JSON is received."""
    def __init__(self):
        super().__init__(401, message="No JSON received. Please check Content-Type.")


class FieldInUseError(CustomError):
    """Error for when a vale property on a model is already in use."""
    def __init__(self, property, **kwargs):
        super().__init__(409, message="{} already in use.".format(property))


class UnauthorizedError(CustomError):
    """Return a generic 401 Unauthorized error."""
    def __init__(self):
        super().__init__(401, message="Unauthorized.")


class NotFoundError(CustomError):
    """Return a generic 404 error."""
    def __init__(self):
        super().__init__(404, message="Not found.")
