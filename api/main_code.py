from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from api.validators import validate_getmeals, validate_listmeals,validate_quality, validate_price
from api.constants import *
import json

with open(MEALS_DATASET_PATH) as f:
    meals_dataset = json.load(f)

# For faster search according to ids of meals and names of ingredients
meals_dict = {meal['id']: meal for meal in meals_dataset['meals']}
ingredients_dict = {ingredient['name'].lower(): ingredient for ingredient in meals_dataset['ingredients']}

meals_and_ingredients_dict  = {}
for meal in meals_dataset['meals']:
    meals_and_ingredients_dict[meal['id']] = {
        'id': meal['id'],
        'name': meal['name'],
        'ingredients': {ingredient['name'].lower(): ingredient for ingredient in meals_dict[meal['id']]['ingredients']}
    }

def query_vegetarian(meal):
    for ingredient in meal['ingredients']:
        ingredient_name = ingredient['name'].lower()
        if 'vegetarian' not in ingredients_dict[ingredient_name]['groups'] \
                and 'vegan' not in ingredients_dict[ingredient_name]['groups']:  # In case of invalid dataset that uses only vegan in groups
            return False
    return True


def query_vegan(meal):
    for ingredient in meal['ingredients']:
        ingredient_name = ingredient['name'].lower()
        if 'vegan' not in ingredients_dict[ingredient_name]['groups']:
            return False
    return True

def convert_quantity(quantity,convert_from,convert_to):
    if convert_from == convert_to:
        return quantity
    elif convert_from == 'kilogram' and convert_to == 'gram' or convert_from == 'millilitre' and convert_to == 'litre':
        return quantity * 1000
    elif convert_from == 'gram' and convert_to == 'kilogram' or convert_from == 'litre' and convert_to == 'millilitre':
        return quantity / 1000


def find_price_of_ingredient(meal_id,ingredient_name,quality):
    ingredient_name = ingredient_name.lower()
    
    ingredient = meals_and_ingredients_dict[meal_id]['ingredients']

    quantity = ingredient[ingredient_name]['quantity']
    quantity_type = ingredient[ingredient_name]['quantity_type']

    for option in ingredients_dict[ingredient_name]['options']:
        if option['quality'] == quality:
            price = option['price']
            per_amount = option['per_amount']
            break

    converted_quantity = convert_quantity(quantity,quantity_type,per_amount)
    final_price = price * converted_quantity
    return final_price


@validate_listmeals
def get_listmeals(query,is_vegetarian=False, is_vegan=False):
    result = []

    for meal in meals_dataset['meals']:
        try:
            if is_vegan and query_vegan(meal) == False:
                continue
            if is_vegetarian and query_vegetarian(meal) == False:
                continue
        except KeyError:
            return {'error': 'Invalid dataset.'}

        meal_object = {
            'id': meal['id'],
            'name': meal['name'],
            'ingredients': [ingredient['name'] for ingredient in meal['ingredients']]
        }
        result.append(meal_object)

    return result


@validate_getmeals
def get_getmeals(query,id):

    id = int(id)

    if meals_dict.get(id) is None:
        return {'error': f'There is no meal that id equals {id}'}, HTTPStatus.BAD_REQUEST
    
    result = {}
    result['id'] = id
    result['name'] = meals_dict[id]['name']
    result['ingredients'] = [ingredients_dict[ingredient['name'].lower()] for ingredient in meals_dict[id]['ingredients']]

    return result
    

@validate_quality   
def post_quality(query,meal_id,query_ingredients_dict):
        
        meal_id = int(meal_id)
        query_ingredients_dict = {ingredient.lower():value.lower() for ingredient,value in query_ingredients_dict.items()} # For case insensitive search

        # If meal does not exist
        if meals_dict.get(meal_id) is None:
            return {'error': f'There is no meal that id equals {meal_id}'}, HTTPStatus.BAD_REQUEST
        
        # If menu does not contain the ingredient
        for ingredient in query_ingredients_dict.keys():
            if ingredients_dict.get(ingredient) is None:
                return {'error': f'There is no ingredient that name equals {ingredient} in the menu'}, HTTPStatus.BAD_REQUEST


        specific_meal_ingredients_dict = meals_and_ingredients_dict[meal_id]['ingredients'] # For case insensitive and faster search according to names of ingredients

        total_result = 0
        for query_ingredient_name,val in query_ingredients_dict.items():
            #  If meal does not contain the ingredient
            if specific_meal_ingredients_dict.get(query_ingredient_name) is None:
                return {'error': f'The meal {meals_dict[meal_id]["name"]} does not contain {query_ingredient_name}'}, HTTPStatus.BAD_REQUEST
            
            if val == 'high':
                total_result += Quality.HIGH.value
            elif val == 'medium':
                total_result += Quality.MEDIUM.value
            elif val == 'low': 
                total_result += Quality.LOW.value
            else:
                return {'error': f'Invalid value for {query_ingredient_name}'}, HTTPStatus.BAD_REQUEST
        
        total_result = (len(specific_meal_ingredients_dict)-len(query_ingredients_dict))*DEFAULT_QUALITY_FOR_QUALITY.value # Default value for ingredients that are not in query is "HIGH"
        total_result = total_result / len(specific_meal_ingredients_dict)
        return {'quality': total_result}


 
@validate_price
def post_price(query,meal_id,query_ingredients_dict):
    meal_id = int(meal_id)
    query_ingredients_dict = {ingredient.lower():value.lower() for ingredient,value in query_ingredients_dict.items()} # For case insensitive search

    # If meal does not exist
    if meals_dict.get(meal_id) is None:
        return {'error': f'There is no meal that id equals {meal_id}'}, HTTPStatus.BAD_REQUEST
    
    # If menu does not contain the ingredient
    for ingredient in query_ingredients_dict.keys():
        if ingredients_dict.get(ingredient) is None:
            return {'error': f'There is no ingredient that name equals {ingredient} in the menu'}, HTTPStatus.BAD_REQUEST

    
    specific_meal_ingredients_dict = meals_and_ingredients_dict[meal_id]['ingredients'] # For case insensitive and faster search according to names of ingredients

    total_result = 0
    high_ingredients = 0
    medium_ingredients = 0
    low_ingredients = 0 

    for query_ingredient_name,val in query_ingredients_dict.items():
        #  If meal does not contain the ingredient
        if specific_meal_ingredients_dict.get(query_ingredient_name) is None:
            return {'error': f'The meal {meals_dict[meal_id]["name"]} does not contain {query_ingredient_name}'}, HTTPStatus.BAD_REQUEST

        if val == 'high':
            high_ingredients += 1
            total_result += find_price_of_ingredient(meal_id,query_ingredient_name,'high')
            
        elif val == 'medium':
            medium_ingredients += 1
            total_result += find_price_of_ingredient(meal_id,query_ingredient_name,'medium')
            
        elif val == 'low':
            low_ingredients += 1
            total_result += find_price_of_ingredient(meal_id,query_ingredient_name,'low')
            
        else:
            return {'error': f'Invalid value for {query_ingredient_name}'}, HTTPStatus.BAD_REQUEST
    
    for meal_ingredient_name in specific_meal_ingredients_dict.keys():
        if query_ingredients_dict.get(meal_ingredient_name) is None:
            total_result += find_price_of_ingredient(meal_id,meal_ingredient_name,DEFAULT_QUALITY_FOR_PRICE)

    total_result += high_ingredients * ADDITIONAL_COST_FOR_HIGH_QUALITY
    total_result += medium_ingredients * ADDITIONAL_COST_FOR_MEDIUM_QUALITY
    total_result += low_ingredients * ADDITIONAL_COST_FOR_LOW_QUALITY


    return {'price': total_result }
      



class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # TODO: config file
    PORT = 8080

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_string = parsed_url.query
        query_params = parse_qs(parsed_url.query)
        try:
            # TODO Burayi asagidaki yorum gibi duzenle
            if parsed_url.path == '/listMeals':
                #TODO: is_vegano gibi queryde duz listmeals donuyo, onu 73-74deki falselari none yapip validatorde handlemak lazim
                is_vegetarian = query_params.get('is_vegetarian', [False])[0]
                is_vegan = query_params.get('is_vegan', [False])[0]
                result = get_listmeals(query_string,is_vegetarian, is_vegan)

            elif parsed_url.path == '/getMeal':
                query_id = query_params.get('id', [None])[0]
                result = get_getmeals(query_string,query_id)

            else:
                self.send_response(404)
                self.end_headers()
                return

        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            self.send_error(500, error_msg)
            return

        # TODO:  her fonksiyon result ve kod donebilir basariliysa 200 hataliysa hata kodu gibi, basarili degilse error end headers, basariliysa awsagida gibi bir ife alinabilir, od urumda try catch kaldirilir
        #TODO Hata versede 200 donuyo ustteki gibi bir duzenleme cozer burayi
        response = json.dumps(result, indent=4).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)
        
    def do_POST(self):
        parsed_url = urlparse(self.path)
        content_length = int(self.headers['Content-Length'])
        query_string = self.rfile.read(content_length).decode()
        query_params = parse_qs(query_string)

        try:
            if parsed_url.path == '/quality':
                meal_id = query_params.get('meal_id', [None])[0]
                query_ingredients = {key.lower():val[0] for key,val in query_params.items() if key != 'meal_id'}   
                result = post_quality(query_string,meal_id,query_ingredients)
            elif parsed_url.path == '/price':
                meal_id = query_params.get('meal_id', [None])[0]
                query_ingredients = {key.lower():val[0] for key,val in query_params.items() if key != 'meal_id'}   
                result = post_price(query_string,meal_id,query_ingredients)
            else:
                self.send_response(404)
                self.end_headers()
                return

        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            self.send_error(500, error_msg)
            return
        response = json.dumps(result, indent=4).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)
















