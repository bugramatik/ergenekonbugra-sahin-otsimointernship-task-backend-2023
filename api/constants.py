from enum import Enum
import json

class Quality(Enum):
    LOW = 10
    MEDIUM = 20
    HIGH = 30

DEFULT_VEGETARIAN_CHOICE = False
DEFAULT_VEGAN_CHOICE = False
MEALS_DATASET_PATH = 'data/meals.json'
DEFAULT_QUALITY_FOR_QUALITY = Quality.HIGH
DEFAULT_QUALITY_FOR_PRICE = 'high'
ADDITIONAL_COST_FOR_LOW_QUALITY = 0.1
ADDITIONAL_COST_FOR_MEDIUM_QUALITY = 0.05
ADDITIONAL_COST_FOR_HIGH_QUALITY = 0.0

# For solving circular import problem we need to wrtie it here
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

