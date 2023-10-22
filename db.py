import pymongo
import datetime
from flask import request
from bson.objectid import ObjectId
import sys
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
    db[LISTING_COLLECTION_NAME].create_index([("tags", 1)])
    db[LISTING_COLLECTION_NAME].create_index([("allergens", 1)])
    db[LISTING_COLLECTION_NAME].create_index([("name", "text")])
    db[USER_COLLECTION_NAME].create_index([("preferences", 1)])
    db[USER_COLLECTION_NAME].create_index([("allergens", 1)])
    db[USER_COLLECTION_NAME].create_index([("email", 1)])
    db[USER_COLLECTION_NAME].create_index([("phone_number", 1)])
    db[TRANSACTION_COLLECTION_NAME].create_index([("reserved_by", 1)])
    db[TRANSACTION_COLLECTION_NAME].create_index([("listing_id", 1)])


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


def add_listing(data):
    return insert(LISTING_COLLECTION_NAME, data)


def edit_listing(data, listing_id):
    return update(
        LISTING_COLLECTION_NAME,
        {'_id': listing_id},
        {'$set': data}
    )


def get_user_data(user_id):
    return find(USER_COLLECTION_NAME, {'_id': user_id})


def get_current_user_data():
    return get_user_data(ObjectId(request.cookies.get(LOGIN_COOKIE_NAME)))

def show_reservations():
    user_id = get_current_user_data()['_id']
    listing_ids = [x.get('listing_id') for x in find_all(
        TRANSACTION_COLLECTION_NAME, {'reserved_by': user_id})]
    return find_all(LISTING_COLLECTION_NAME, {'_id': {'$in': listing_ids}})


def delete(collection, query):
    return db[collection].delete_one(query)

def find_listings(match_query, sort_query=None):
    user_data = get_current_user_data()
    user_latitude, user_longitude = user_data.get('location').get('coordinates')
    
    if user_latitude == 0 and user_longitude == 0:
        cursor = find_all(LISTING_COLLECTION_NAME, match_query)
        if sort_query:
            cursor = cursor.sort(sort_query.keys()[0], sort_query.values()[0])
        
        return list(cursor)
    else:
        q = [{
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [user_latitude, user_longitude]
                    },
                    "distanceField": "distance",
                    "spherical": True
                }
            },
            {
                "$match": match_query
            },
        ]

        if sort_query:
            q.append({"$sort": sort_query})

        results = list(db[LISTING_COLLECTION_NAME].aggregate(q))

        for item in results:
            if item['location']['coordinates'] == [0, 0]:
                item['distance'] = None
        
        if sort_query and 'distance' in sort_query:
            results.sort(key = lambda x : sys.maxsize if x.get('distance') == None else x.get('distance')) 

        return results