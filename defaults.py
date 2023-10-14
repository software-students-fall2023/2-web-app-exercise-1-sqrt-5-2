from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

ROOT_DIR = Path(__file__).parent
TEMPLATES_DIR = ROOT_DIR / 'templates'
STATIC_DIR = ROOT_DIR / 'static'
DATA_DIR = STATIC_DIR / 'data'

MONGO_DB_HOST = os.getenv('MONGO_DB_HOST')
MONGO_DB_PORT = int(os.getenv('MONGO_DB_PORT'))
MONGO_DB_USERNAME = os.getenv('MONGO_DB_USERNAME')
MONGO_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')
USER_COLLECTION_NAME = 'users'
LISTING_COLLECTION_NAME = 'listings'

LOGIN_COOKIE_NAME = 'session'



