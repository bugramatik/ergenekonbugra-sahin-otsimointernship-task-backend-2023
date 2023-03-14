from api.constants import *


def query_vegetarian(meal):
    for ingredient in meal['ingredients']:
        ingredient_name = ingredient['name'].lower()
        if 'vegetarian' not in ingredients_dict[ingredient_name]['groups'] \
                and 'vegan' not in ingredients_dict[ingredient_name][
            'groups']:  # In case of invalid dataset that uses only vegan in groups
            return False
    return True


def query_vegan(meal):
    for ingredient in meal['ingredients']:
        ingredient_name = ingredient['name'].lower()
        if 'vegan' not in ingredients_dict[ingredient_name]['groups']:
            return False
    return True


def convert_quantity(quantity, convert_from, convert_to):
    if convert_from == convert_to:
        return quantity
    elif (convert_from == 'kilogram' and convert_to == 'gram') or (
            convert_from == 'litre' and convert_to == 'millilitre'):
        return quantity * 1000
    elif (convert_from == 'gram' and convert_to == 'kilogram') or (
            convert_from == 'millilitre' and convert_to == 'litre'):
        return quantity / 1000
    raise Exception('Invalid convert_from or convert_to: Dataset can be erroneous', convert_from, convert_to)


def find_price_of_ingredient(meal_id, ingredient_name, quality):
    ingredient_name = ingredient_name.lower()
    ingredient = meals_and_ingredients_dict[meal_id]['ingredients']
    quantity = ingredient[ingredient_name]['quantity']
    quantity_type = ingredient[ingredient_name]['quantity_type']

    for option in ingredients_dict[ingredient_name]['options']:
        if option['quality'] == quality:
            price = option['price']
            per_amount = option['per_amount']
            break

    converted_quantity = convert_quantity(quantity, quantity_type, per_amount)
    final_price = price * converted_quantity
    return final_price


def find_price_of_meal(meal_id, query_ingredients_dict={}):
    specific_meal_ingredients_dict = meals_and_ingredients_dict[meal_id][
        'ingredients']  # For case insensitive and faster search according to names of ingredients
    total_result = 0
    high_ingredients = 0
    medium_ingredients = 0
    low_ingredients = 0

    for query_ingredient_name, val in query_ingredients_dict.items():

        #  If meal does not contain the ingredient
        if specific_meal_ingredients_dict.get(query_ingredient_name) is None:
            raise Exception('Invalid dataset: Meal does not contain the ingredient', meal_id, query_ingredient_name)

        if val == 'high':
            high_ingredients += 1
            total_result += find_price_of_ingredient(meal_id, query_ingredient_name, 'high')

        elif val == 'medium':
            medium_ingredients += 1
            total_result += find_price_of_ingredient(meal_id, query_ingredient_name, 'medium')

        elif val == 'low':
            low_ingredients += 1
            total_result += find_price_of_ingredient(meal_id, query_ingredient_name, 'low')

        else:
            raise Exception('Invalid value for ingredient')

    for meal_ingredient_name in specific_meal_ingredients_dict.keys():
        if query_ingredients_dict.get(meal_ingredient_name) is None:
            total_result += find_price_of_ingredient(meal_id, meal_ingredient_name, DEFAULT_QUALITY_FOR_PRICE)

    total_result += high_ingredients * ADDITIONAL_COST_FOR_HIGH_QUALITY
    total_result += medium_ingredients * ADDITIONAL_COST_FOR_MEDIUM_QUALITY
    total_result += low_ingredients * ADDITIONAL_COST_FOR_LOW_QUALITY
    return round(total_result, 2)


def find_quality_of_meal(meal_id, query_ingredients_dict={}):
    specific_meal_ingredients_dict = meals_and_ingredients_dict[meal_id][
        'ingredients']  # For case insensitive and faster search according to names of ingredients

    total_result = 0
    for query_ingredient_name, val in query_ingredients_dict.items():
        #  If meal does not contain the ingredient
        if specific_meal_ingredients_dict.get(query_ingredient_name) is None:
            raise Exception('Invalid dataset: Meal does not contain the ingredient', meal_id, query_ingredient_name)

        if val == 'high':
            total_result += Quality.HIGH.value
        elif val == 'medium':
            total_result += Quality.MEDIUM.value
        elif val == 'low':
            total_result += Quality.LOW.value
        else:
            raise Exception('Invalid value for ingredient ', query_ingredient_name)

    total_result += (len(specific_meal_ingredients_dict) - len(
        query_ingredients_dict)) * DEFAULT_QUALITY_FOR_QUALITY.value  # Default value for ingredients that are not in query is "HIGH"
    total_result = total_result / len(specific_meal_ingredients_dict)
    return round(total_result, 2)
