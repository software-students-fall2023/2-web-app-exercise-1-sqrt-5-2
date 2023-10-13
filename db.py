import pymongo
from bson.objectid import ObjectId
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_DB_HOST = os.getenv('MONGO_DB_HOST')
MONGO_DB_PORT = os.getenv('MONGO_DB_PORT')
MONGO_DB_USERNAME = os.getenv('MONGO_DB_USERNAME')
MONGO_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')

# make a connection to the database server

connection = pymongo.MongoClient(MONGO_DB_HOST, MONGO_DB_PORT,
                                username = MONGO_DB_USERNAME,
                                password = MONGO_DB_PASSWORD,
                                authSource = DATABASE_NAME)

# select a specific database on the server
db = connection[DATABASE_NAME]