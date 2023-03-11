from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from api.validators import validate_getmeals, validate_listmeals
import json

with open('data/meals.json') as f:
    meals_dataset = json.load(f)

# For faster search according to ids of meals and names of ingredients
meals_dict = {meal['id']: meal for meal in meals_dataset['meals']}
ingredients_dict = {
    ingredient['name']: ingredient for ingredient in meals_dataset['ingredients']}


def query_vegetarian(meal):
    for ingredient in meal['ingredients']:
        ingredient_name = ingredient['name']
        if 'vegetarian' not in ingredients_dict[ingredient_name]['groups'] \
                and 'vegan' not in ingredients_dict[ingredient_name]['groups']:  # In case of invalid dataset that uses only vegan in groups
            return False
    return True


def query_vegan(meal):
    for ingredient in meal['ingredients']:
        ingredient_name = ingredient['name']
        if 'vegan' not in ingredients_dict[ingredient_name]['groups']:
            return False
    return True

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
        return {'error': f'There is no meal that id equals {id}'}, HTTPStatus.INTERNAL_SERVER_ERROR
    return meals_dict[id]
    


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

            elif parsed_url.path == '/getMeals':
                query_id = query_params.get('id', [None])[0]
                result = get_getmeals(query_string,query_id)

            else:
                self.send_response(404)
                self.end_headers()
                return

        except ValueError as e:
            error_msg = f"Invalid parameter value: {str(e)}"
            self.send_error(400, error_msg)
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
