import pymongo
import datetime
from flask import request
from bson.objectid import ObjectId
from defaults import (
    MONGO_DB_HOST,
    MONGO_DB_PORT,
    MONGO_DB_USERNAME,
    MONGO_DB_PASSWORD,
    DATABASE_NAME,
    USER_COLLECTION_NAME,
    LOGIN_COOKIE_NAME
)

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

def get_user_data(user_id):
    return find(USER_COLLECTION_NAME, {'_id': user_id})

def get_current_user_data():
    return get_user_data(ObjectId(request.cookies.get(LOGIN_COOKIE_NAME)))
    