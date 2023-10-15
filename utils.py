from db import insert, find, find_all
from flask_bcrypt import Bcrypt
from flask import request, redirect, url_for
from functools import wraps
from defaults import LOGIN_COOKIE_NAME, USER_COLLECTION_NAME, LISTING_COLLECTION_NAME


def requires_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.cookies.get(LOGIN_COOKIE_NAME):
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


def register_user(form_data):
    first_name = form_data.get('first_name')
    last_name = form_data.get('last_name')
    email = form_data.get('email')
    password = form_data.get('password')
    password2 = form_data.get('password2')

    if password != password2:
        raise Exception('Passwords do not match!')

    password = Bcrypt().generate_password_hash(password).decode('utf-8')

    result = find(USER_COLLECTION_NAME, {'email': email})
    if result:
        raise Exception('User with that email already exists!')

    insert(
        USER_COLLECTION_NAME,
        {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password
        }
    )


def login_user(form_data):
    result = find(USER_COLLECTION_NAME, {'email': form_data.get('email')})
    if not result:
        raise Exception('User with that email does not exist!')

    if not Bcrypt().check_password_hash(result.get('password'), form_data.get('password')):
        raise Exception('Incorrect password!')

    return result.get('_id')


def show_listings(query):
    return find_all('listings', query)

def add_listing(form_data):
    
    insert(
        LISTING_COLLECTION_NAME,
        {
            'name': form_data.get('food-name'),
            'quantity': form_data.get('quantity'),
            'category': form_data.get('food-category'),
            'expiry': form_data.get('expiration-date'),
            'photo': form_data.get('food-photo'),
            'comments' : form_data.get('food-comments')
        }
    )
