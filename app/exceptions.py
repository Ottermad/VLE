class CustomError(Exception):
    """Custom Error that contains a status code and can be easily converted to json."""
    def __init__(self, status_code, **kwargs):
        self.status_code = status_code
        self.kwargs = kwargs

    def to_dict(self):
        return {'status_code': self.status_code, 'error': True, **self.kwargs}
