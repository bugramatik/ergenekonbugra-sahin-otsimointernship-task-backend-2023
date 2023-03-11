from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from validators import validate_id
import socketserver
import json

with open('../data/meals.json') as f:
    meals_dataset = json.load(f)

# For faster search according to ids of meals and names of ingredients
meals_dict = {meal['id']: meal for meal in meals_dataset['meals']}
ingredients_dict = {ingredient['name']: ingredient for ingredient in meals_dataset['ingredients']}


def query_vegetarian(meal):
    for ingredient in meal['ingredients']:
        ingredient_name = ingredient['name']
        if 'vegetarian' not in ingredients_dict[ingredient_name]['groups'] \
                and 'vegan' not in ingredients_dict[ingredient_name]['groups']: # In case of invalid dataset that uses only vegan in groups
            return False
    return True


def query_vegan(meal):
    for ingredient in meal['ingredients']:
        ingredient_name = ingredient['name']
        if 'vegan' not in ingredients_dict[ingredient_name]['groups']:
            return False
    return True



def get_listmeals(is_vegetarian=False, is_vegan=False):
    #TODO: Validator
    result = []

    for meal in meals_dataset['meals']:
        try:
            if is_vegan and query_vegan(meal) == False:
                continue
            if is_vegetarian and query_vegetarian(meal) == False:
                continue
        except KeyError:
            return {'error': 'Error: Invalid dataset.'}

        meal_object = {
            'id': meal['id'],
            'name': meal['name'],
            'ingredients': [ingredient['name'] for ingredient in meal['ingredients']]
        }
        result.append(meal_object)

    return result

@validate_id
def get_getmeals(id):
    id = int(id)
    return meals_dict[id]

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    #TODO: config file
    PORT = 8080

    with open('../data/meals.json', 'r') as f:
        meals = json.load(f)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        try:
            if parsed_url.path == '/listMeals':
                is_vegetarian = query_params.get('is_vegetarian', ['false'])[0] == 'true'
                is_vegan = query_params.get('is_vegan', ['false'])[0] == 'true'
                result = get_listmeals(is_vegetarian, is_vegan)
            elif parsed_url.path == '/getMeals':
                query_id = query_params.get('id')
                result = get_getmeals(query_id)
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

        response = json.dumps(result, indent=4).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)

    
