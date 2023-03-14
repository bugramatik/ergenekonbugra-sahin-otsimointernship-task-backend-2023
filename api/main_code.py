import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from api.constants import *
from api.endpoints import get_listmeals, get_getmeals, post_quality, post_price, post_random


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # TODO: config file

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_string = parsed_url.query
        query_params = parse_qs(parsed_url.query)
        try:
            if parsed_url.path == '/listMeals':
                is_vegetarian = query_params.get('is_vegetarian', [DEFULT_VEGETARIAN_CHOICE])[0]
                is_vegan = query_params.get('is_vegan', [DEFAULT_VEGAN_CHOICE])[0]
                result, status = get_listmeals(query_string, is_vegetarian, is_vegan)

            elif parsed_url.path == '/getMeal':
                query_id = query_params.get('id', [None])[0]
                result, status = get_getmeals(query_string, query_id)

            elif parsed_url.path == '/getRandom':
                budget = query_params.get('budget', [None])[0]
                result, status = post_random(query_string, budget)

            else:
                self.send_response(404)
                self.end_headers()
                return

        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            self.send_error(500, error_msg)
            return

        response = json.dumps(result, indent=4).encode()
        self.send_response(status)
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
                query_ingredients = {key.lower(): val[0] for key, val in query_params.items() if key != 'meal_id'}
                result, status = post_quality(query_string, meal_id, query_ingredients)
            elif parsed_url.path == '/price':
                meal_id = query_params.get('meal_id', [None])[0]
                query_ingredients = {key.lower(): val[0] for key, val in query_params.items() if key != 'meal_id'}
                result, status = post_price(query_string, meal_id, query_ingredients)
            elif parsed_url.path == '/random':
                budget = query_params.get('budget', [None])[0]
                result, status = post_random(query_string, budget)
            else:
                self.send_response(404)
                self.end_headers()
                return

        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            self.send_error(500, error_msg)
            return
        response = json.dumps(result, indent=4).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)
