import pymongo
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_DB_HOST = os.getenv('MONGO_DB_HOST')
MONGO_DB_PORT = int(os.getenv('MONGO_DB_PORT'))
MONGO_DB_USERNAME = os.getenv('MONGO_DB_USERNAME')
MONGO_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')

# make a connection to the database server
connection = pymongo.MongoClient(
    MONGO_DB_HOST,
    MONGO_DB_PORT,

    # uncomment if you have a username and password on the database server
    # username=MONGO_DB_USERNAME,
    # password=MONGO_DB_PASSWORD,
)

# select a specific database on the server
db = connection[DATABASE_NAME]

def insert(collection, item):
    return db[collection].insert_one({**item, 'created_at': datetime.datetime.now()})

def insert_all(collection, item_array):  
    for item in item_array:
        insert(collection, item)
    
def find(collection, query):
    return db[collection].find_one(query)

def find_all(collection, query):
    return db[collection].find(query)
