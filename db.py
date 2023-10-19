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
    LOGIN_COOKIE_NAME,
    LISTING_COLLECTION_NAME,
    TRANSACTION_COLLECTION_NAME
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


def create_index():
    db[LISTING_COLLECTION_NAME].create_index([("location", "2dsphere")])
    db[LISTING_COLLECTION_NAME].create_index([("name", "text")])


def drop_collection(collection):
    db[collection].drop()


def insert(collection, item):
    return db[collection].insert_one({**item, 'created_at': datetime.datetime.now()})

def insert_all(collection, item_array):
    for item in item_array:
        insert(collection, item)

def find(collection, query):
    return db[collection].find_one(query)

def find_all(collection, query):
    return db[collection].find(query)


def sort(collection, field, query, order=1):
    return db[collection].find(query).sort(field, order)


def update(collection, query, update):
    return db[collection].update_one(query, update)


def get_user_data(user_id):
    return find(USER_COLLECTION_NAME, {'_id': user_id})


def get_current_user_data():
    return get_user_data(ObjectId(request.cookies.get(LOGIN_COOKIE_NAME)))


def get_nearest(user_latitude, user_longitude):
    nearest_locations = db[LISTING_COLLECTION_NAME].aggregate([
        {
            "$geoNear": {
                "near": {
                    "type": "Point",
                    "coordinates": [user_longitude, user_latitude]
                },
                "distanceField": "distance",
                "spherical": True
            }
        }
    ])

    return nearest_locations

def show_reservations():
    user_id = get_current_user_data()['_id']
    listing_ids = [x.get('listing_id') for x in find_all(TRANSACTION_COLLECTION_NAME, {'reserved_by': user_id})]
    return find_all(LISTING_COLLECTION_NAME, {'_id': {'$in': listing_ids}})

def delete(collection, query):
    return db[collection].delete_one(query)