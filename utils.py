from db import insert, find, find_all, get_current_user_data, update
from flask_bcrypt import Bcrypt
from flask import request, redirect, url_for, render_template
from functools import wraps
from defaults import LOGIN_COOKIE_NAME, USER_COLLECTION_NAME, LISTING_COLLECTION_NAME


def requires_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.cookies.get(LOGIN_COOKIE_NAME):
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


def redirect_if_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.cookies.get(LOGIN_COOKIE_NAME):
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapper


def check_confirm_password(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if password != password2:
            raise Exception('Passwords do not match!')
        return func(*args, **kwargs)
    return wrapper


def validate_unique(key):
    def _validate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            query = {key: request.form.get(key)}

            current_user = get_current_user_data()
            if current_user:
                query['_id'] = {'$ne': current_user.get('_id')}

            result = find(USER_COLLECTION_NAME, query)
            if result:
                name = key.replace('_', ' ').capitalize()
                raise Exception(f'{name} has already been taken!')

            return func(*args, **kwargs)
        return wrapper
    return _validate


def check_password(hash, password):
    if not Bcrypt().check_password_hash(hash, password):
        raise Exception('Incorrect password!')


@validate_unique('email')
@check_confirm_password
def register_user(form):
    # hash the password
    password = Bcrypt().generate_password_hash(
        form.get('password')).decode('utf-8')

    insert(
        USER_COLLECTION_NAME,
        {
            'first_name': form.get('first_name'),
            'last_name': form.get('last_name'),
            'email': form.get('email'),
            'password': password,
            'phone_number': "",
            'address': {
                'street': "",
                'city': "",
                'state': "",
                'zipcode': ""
            },
            'preferences': [],
            'setup_complete': False
        }
    )


def login_user(form):
    result = find(USER_COLLECTION_NAME, {'email': form.get('email')})
    if not result:
        raise Exception('User with that email does not exist!')

    check_password(result.get('password'), form.get('password'))

    return result.get('_id'), result.get('setup_complete')


@validate_unique('email')
@validate_unique('phone_number')
def update_user_data(form):
    update(
        USER_COLLECTION_NAME,
        {'_id': get_current_user_data().get('_id')},
        {
            '$set': {
                'first_name': form.get('first_name'),
                'last_name': form.get('last_name'),
                'email': form.get('email'),
                'phone_number': form.get('phone_number'),
                'address': {
                    'street': form.get('street'),
                    'city': form.get('city'),
                    'state': form.get('state'),
                    'zipcode': form.get('zipcode')
                },
                'preferences': form.getlist('preferences'),
                'setup_complete': all(form.values())
            }
        }
    )
    return render_template('profile.html', user=get_current_user_data(), tags=get_user_preferences(), message='Profile updated successfully!')


@check_confirm_password
def change_password(form):
    current_user = get_current_user_data()
    check_password(current_user.get('password'), form.get('old_password'))

    update(
        USER_COLLECTION_NAME,
        {'_id': current_user.get('_id')},
        {
            '$set': {
                'password': Bcrypt().generate_password_hash(form.get('password')).decode('utf-8')
            }
        }
    )
    return render_template('profile.html', user=get_current_user_data(), tags=get_user_preferences(), message='Password changed successfully!')


def edit_profile(form, func):
    try:
        return func(form)
    except Exception as e:
        return render_template('profile.html', user=get_current_user_data(), tags=get_user_preferences(), error=e)


def get_user_preferences():
    result = {tag: False for listing in find_all(
        LISTING_COLLECTION_NAME, {}) for tag in listing.get('tags', [])}
    for tag in get_current_user_data().get('preferences'):
        result[tag] = True
    result = [{'name': tag, 'selected': selected}
              for tag, selected in result.items()]

    return sorted(result, key=lambda x: x.get('name'))


def show_listings(query):
    return find_all('listings', query)


def add_listing(form):
    insert(
        LISTING_COLLECTION_NAME,
        {
            'name': form.get('food-name'),
            'quantity': form.get('quantity'),
            'category': form.get('food-category'),
            'expiry': form.get('expiration-date'),
            'photo': form.get('food-photo'),
            'comments': form.get('food-comments')
        }
    )
