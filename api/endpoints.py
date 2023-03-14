import random
from http import HTTPStatus

from api.utils import *
from api.validators import validate_getmeals, validate_listmeals, validate_quality, validate_price, validate_random


@validate_listmeals
def get_listmeals(query, is_vegetarian=False, is_vegan=False):
    result = []

    for meal in meals_dataset['meals']:
        try:
            if is_vegan and query_vegan(meal) == False:
                continue
            if is_vegetarian and query_vegetarian(meal) == False:
                continue
        except KeyError:
            return {'error': 'Invalid dataset.'}, HTTPStatus.INTERNAL_SERVER_ERROR

        meal_object = {
            'id': meal['id'],
            'name': meal['name'],
            'ingredients': [ingredient['name'] for ingredient in meal['ingredients']]
        }
        result.append(meal_object)

    return result, HTTPStatus.OK


@validate_getmeals
def get_getmeals(query, id):
    id = int(id)

    if meals_dict.get(id) is None:
        return {'error': f'There is no meal that id equals {id}'}, HTTPStatus.BAD_REQUEST

    result = {}
    result['id'] = id
    result['name'] = meals_dict[id]['name']
    result['ingredients'] = [ingredients_dict[ingredient['name'].lower()] for ingredient in
                             meals_dict[id]['ingredients']]

    return result, HTTPStatus.OK


@validate_quality
def post_quality(query, meal_id, query_ingredients_dict):
    meal_id = int(meal_id)
    query_ingredients_dict = {ingredient.lower(): value.lower() for ingredient, value in
                              query_ingredients_dict.items()}  # For case insensitive search

    # If meal does not exist
    if meals_dict.get(meal_id) is None:
        return {'error': f'There is no meal that id equals {meal_id}'}, HTTPStatus.BAD_REQUEST

    # If menu does not contain the ingredient
    for ingredient in query_ingredients_dict.keys():
        if ingredients_dict.get(ingredient) is None:
            return {
                'error': f'There is no ingredient that name equals {ingredient} in the menu'}, HTTPStatus.BAD_REQUEST

    try:
        quality = find_quality_of_meal(meal_id, query_ingredients_dict)
    except Exception as e:
        return {'error': str(e)}, HTTPStatus.BAD_REQUEST
    return {'quality': quality}, HTTPStatus.OK


@validate_price
def post_price(query, meal_id, query_ingredients_dict):
    meal_id = int(meal_id)
    query_ingredients_dict = {ingredient.lower(): value.lower() for ingredient, value in
                              query_ingredients_dict.items()}  # For case insensitive search

    # If meal does not exist
    if meals_dict.get(meal_id) is None:
        return {'error': f'There is no meal that id equals {meal_id}'}, HTTPStatus.BAD_REQUEST

    # If menu does not contain the ingredient
    for ingredient in query_ingredients_dict.keys():
        if ingredients_dict.get(ingredient) is None:
            return {
                'error': f'There is no ingredient that name equals {ingredient} in the menu'}, HTTPStatus.BAD_REQUEST
    try:
        price = find_price_of_meal(meal_id, query_ingredients_dict)
    except Exception as e:
        return {'error': str(e)}, HTTPStatus.BAD_REQUEST
    return {'price': round(price, 2)}, HTTPStatus.OK


@validate_random
def post_random(query, budget):
    random_meal = {}
    if budget is None:
        # Default case: we just return a random meal with random qualities
        random_meal = random.choice(list(meals_dict.values()))
        random_ingredient_quality_dict = {}
        for ingredient in random_meal['ingredients']:
            random_quality = random.choice(['high', 'medium', 'low'])
            random_ingredient_quality_dict[ingredient['name'].lower()] = random_quality

        price = find_price_of_meal(random_meal['id'], random_ingredient_quality_dict)
        quality = find_quality_of_meal(random_meal['id'], random_ingredient_quality_dict)

        result_ingredients_list = []
        for ingredient in random_meal['ingredients']:
            result_ingredients_list.append(
                {'name': ingredient['name'], 'quality': random_ingredient_quality_dict[ingredient['name'].lower()]})

        return {
            'id': random_meal['id'],
            'name': random_meal['name'],
            'price': round(price, 2),
            'quality_score': quality,
            'ingredients': result_ingredients_list
        }, HTTPStatus.OK

    budget = float(budget)
    meals_list = list(meals_dict.values())

    while True:
        if len(meals_list) == 0:
            return {'error': 'There is no meal that fits the budget'}, HTTPStatus.BAD_REQUEST
        unused_ingredient_combinations = {}

        random_meal = random.choice(meals_list)
        meals_list.remove(random_meal)

        for ingredient in random_meal['ingredients']:
            unused_ingredient_combinations[ingredient['name'].lower()] = ['high', 'medium', 'low']

        query_ingridient = {}
        for ingredient, unused_qualities in unused_ingredient_combinations.items():
            random_quality = random.choice(
                unused_qualities)  # Choose a random quality from the unused qualities of the ingredient
            query_ingridient[
                ingredient.lower()] = random_quality  # Add the quality to the query_ingridient_dict for sending to the find_price_of_meal function
            unused_qualities.remove(
                random_quality)  # Remove the quality that is used so that combination algorithm does not use it again

        price = find_price_of_meal(random_meal['id'], query_ingridient)
        quality_score = find_quality_of_meal(random_meal['id'], query_ingridient)

        formatted_ingredient_list = []
        for ingredient, quality in query_ingridient.items():
            formatted_ingredient_list.append({'name': ingredient, 'quality': quality})

        if price < budget:
            return {
                'id': random_meal['id'],
                'name': random_meal['name'],
                'price': round(price, 2),
                'quality_score': quality_score,
                'ingredients': formatted_ingredient_list
            }, HTTPStatus.OK
