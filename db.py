import datetime
import pymongo
import sys
from bson.objectid import ObjectId
from flask import request

from defaults import (
    MONGO_DB_HOST,
    MONGO_DB_PORT,
    MONGO_DB_USERNAME,
    MONGO_DB_PASSWORD,
    DATABASE_NAME,
    USER_COLLECTION_NAME,
    LOGIN_COOKIE_NAME,
    LISTING_COLLECTION_NAME,
    TRANSACTION_COLLECTION_NAME,
    ALLERGENS
)

# make a connection to the database server
if MONGO_DB_USERNAME and MONGO_DB_PASSWORD:
    connection = pymongo.MongoClient(
        MONGO_DB_HOST,
        MONGO_DB_PORT,
        username=MONGO_DB_USERNAME,
        password=MONGO_DB_PASSWORD,
        authSource=DATABASE_NAME,
    )
else:
    connection = pymongo.MongoClient(
        MONGO_DB_HOST,
        MONGO_DB_PORT
    )

# select a specific database on the server
db = connection[DATABASE_NAME]


def create_index():
    db[LISTING_COLLECTION_NAME].create_index([("location", "2dsphere")])
    db[LISTING_COLLECTION_NAME].create_index([("tags", 1)])
    db[LISTING_COLLECTION_NAME].create_index([("name", "text")])
    db[LISTING_COLLECTION_NAME].create_index([("user_id", 1)])

    db[USER_COLLECTION_NAME].create_index([("location", "2dsphere")])
    db[USER_COLLECTION_NAME].create_index([("preferences", 1)])
    db[USER_COLLECTION_NAME].create_index([("email", 1)])
    db[USER_COLLECTION_NAME].create_index([("phone_number", 1)])

    for allergen in ALLERGENS:
        db[LISTING_COLLECTION_NAME].create_index([(f'allergens.{allergen}', 1)])
        db[USER_COLLECTION_NAME].create_index([(f'allergens.{allergen}', 1)])

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


def delete_all(collection, query):
    return db[collection].delete_many(query)


def find_listings(match_query, sort_query=None):
    user_data = get_current_user_data()
    user_latitude, user_longitude = user_data.get('location').get('coordinates')

    if user_latitude == 0 and user_longitude == 0:
        cursor = find_all(LISTING_COLLECTION_NAME, match_query)
        if sort_query:
            (sortby, order), = sort_query.items()
            cursor = cursor.sort(sortby, order)

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
            results.sort(key=lambda x: sys.maxsize if x.get('distance') == None else x.get('distance'))

        return results
