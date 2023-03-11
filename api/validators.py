def validate_id(func):
    def wrapper(*args, **kwargs):
        id = kwargs.get('id')
        if not id:
            raise MissingParameterError("ID parameter is missing")
        try:
            int(id)
        except ValueError:
            raise InvalidParameterError("ID parameter should be an integer")
        return func(*args, **kwargs)
    return wrapper