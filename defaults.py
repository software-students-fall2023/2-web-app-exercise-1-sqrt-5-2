from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

ROOT_DIR = Path(__file__).parent
TEMPLATES_DIR = ROOT_DIR / 'templates'
STATIC_DIR = ROOT_DIR / 'static'
DATA_DIR = STATIC_DIR / 'data'
IMAGE_DIR = STATIC_DIR / 'images'

MONGO_DB_HOST = os.getenv('MONGO_DB_HOST')
MONGO_DB_PORT = int(os.getenv('MONGO_DB_PORT'))
MONGO_DB_USERNAME = os.getenv('MONGO_DB_USERNAME')
MONGO_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')
USER_COLLECTION_NAME = 'users'
LISTING_COLLECTION_NAME = 'listings'
TRANSACTION_COLLECTION_NAME = 'transactions'

LOGIN_COOKIE_NAME = 'session'

# food allergens
ALLERGENS = ["Milk", "Eggs", "Fish", "Crustacean shellfish",
             "Tree nuts", "Peanuts", "Wheat", "Soybeans", "Sesame"]

SORT_FUNCTION_FIELDS = {
    'newest': 'date',
    'priceLH': 'price',
    'priceHL': 'price'
}

SORT_FUNCTION_ORDER = {
    'newest': 1,
    'priceLH': 1,
    'priceHL': -1
}

FILTER_FUNCTION_FIELDS = {
    '_5': {
        '$lt': 5
    },
    '5_10': {
        '$gte': 5,
        '$lt': 10
    },
    '10_15': {
        '$gte': 10,
        '$lt': 15
    },
    '15_20': {
        '$gte': 15,
        '$lt': 20
    },
    '20_': {
        '$gte': 5
    },
}
