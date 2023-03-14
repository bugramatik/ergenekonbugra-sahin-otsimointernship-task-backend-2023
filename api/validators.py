import re
from http import HTTPStatus


def validate_listmeals(func):
    def wrapper(*args, **kwargs):

        query_string = args[0]

        if re.match(r"^$", query_string):
            # Default case
            return func(*args, **kwargs)

        elif re.match(r"^is_vegan=(true|false)($|&is_vegetarian=(true|false))$", query_string):
            # Successful case
            return func(*args, **kwargs)

        elif re.match(r"^is_vegetarian=(true|false)($|&is_vegan=(true|false))$", query_string):
            # Successful case
            return func(*args, **kwargs)

        else:
            # Case of there is no id parameter
            return {'error': 'parameter/s or values are wrong'}, HTTPStatus.BAD_REQUEST

    return wrapper


def validate_getmeals(func):
    def wrapper(*args, **kwargs):

        query_string = args[0]

        if re.match(r"^id=(\d+)$", query_string):
            # Succesful case
            return func(*args, **kwargs)

        elif re.match(r"^id=$", query_string):
            # Case of query is "id="
            return {'error': 'id value is missing'}, HTTPStatus.BAD_REQUEST

        elif re.match(r"^id=.*$", query_string):
            # Case of id value is not integer
            return {'error': 'id parameter is not a valid integer'}, HTTPStatus.BAD_REQUEST

        else:
            # Case of there is no id parameter
            return {'error': 'id parameter is missing'}, HTTPStatus.BAD_REQUEST

    return wrapper


def validate_quality(func):
    def wrapper(*args, **kwargs):

        query_string = args[0]

        if re.match(r"^meal_id=(\d+)($|&)", query_string):
            # Succesful case
            return func(*args, **kwargs)

        else:
            # Ingredients' validation check in the function
            return {'error': 'meal_id is missing or not number'}, HTTPStatus.BAD_REQUEST

    return wrapper


def validate_price(func):
    def wrapper(*args, **kwargs):

        query_string = args[0]

        if re.match(r"^meal_id=(\d+)($|&)", query_string):
            # Succesful case
            return func(*args, **kwargs)

        else:
            # Ingredients' validation check in the function
            return {'error': 'meal_id is missing or not number'}, HTTPStatus.BAD_REQUEST

    return wrapper


def validate_random(func):
    def wrapper(*args, **kwargs):

        query_string = args[0]
        if query_string == '' or re.match(r"^budget=[\d\.]+$", query_string):
            # Succesful case
            return func(*args, **kwargs)

        else:
            # Ingredients' validation check in the function
            return {'error': 'parameter budget is wrong'}, HTTPStatus.BAD_REQUEST

    return wrapper
