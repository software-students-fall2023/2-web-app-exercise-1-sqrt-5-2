from db import insert, update, find, find_all, get_current_user_data, add_listing, edit_listing, find_listings
from flask_bcrypt import Bcrypt
from flask import request, redirect, url_for, render_template
from functools import wraps
from defaults import LOGIN_COOKIE_NAME, USER_COLLECTION_NAME, LISTING_COLLECTION_NAME, ALLERGENS, IMAGE_DIR
from datetime import datetime
from werkzeug.utils import secure_filename
from geopy.geocoders import Nominatim


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


def get_latitude_longitude(street, city, state, zipcode):
    try:
        geolocator = Nominatim(user_agent="foodshare")
        location = geolocator.geocode(
            f'{street}, {city}, {state} {zipcode}', timeout=200)
        coordinates = [location.latitude, location.longitude]
    except Exception as e:
        coordinates = [0, 0]

    return {
        "type": "Point",
        "coordinates": coordinates
    }


@validate_unique('email')
@check_confirm_password
def register_user(form):
    if not all(form.values()):
        raise Exception('Please fill out all fields!')

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
            "location": {
                "type": "Point",
                "coordinates": [0, 0]
            },
            'preferences': [],
            'allergens': {allergen: False for allergen in ALLERGENS},
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
    allergens = {allergen: False for allergen in ALLERGENS}
    for allergen in form.getlist('allergens'):
        allergens[allergen] = True

    data = {
        'first_name': form.get('first_name'),
        'last_name': form.get('last_name'),
        'email': form.get('email'),
        'phone_number': form.get('phone_number'),
        'preferences': form.getlist('preferences'),
    }

    address = {
        'street': form.get('street'),
        'city': form.get('city'),
        'state': form.get('state'),
        'zipcode': form.get('zipcode'),
    }

    data['setup_complete'] = all(data.values()) and all(
        address.values()) and any(allergens.values())
    data['allergens'] = allergens
    data['address'] = address
    data['location'] = get_latitude_longitude(**data['address'])

    update(
        USER_COLLECTION_NAME,
        {'_id': get_current_user_data().get('_id')},
        {'$set': data}
    )
    return render_template('profile.html', user=get_current_user_data(), tags=get_tags(user_preference=True), message='Profile updated successfully!')


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
    return render_template('profile.html', user=get_current_user_data(), tags=get_tags(user_preference=True), message='Password changed successfully!')


def current_tags_and_allergens(tag_form_key='tags', allergen_form_key='allergens'):
    tags = get_tags()
    for tag in request.form.getlist(tag_form_key):
        tags[tag] = True

    allergens = get_allergens()
    for allergen in request.form.getlist(allergen_form_key):
        allergens[allergen] = True

    return tags, allergens


def edit_profile(form, func):
    try:
        return func(form)
    except Exception as e:
        tags, allergens = current_tags_and_allergens(
            tag_form_key='preferences')

        current_data = {
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
            'allergens': allergens,
        }
        return render_template('profile.html', user=current_data, tags=tags, error=e)


def get_tags(user_preference=False, tag_list=None):
    result = {tag: False for listing in find_all(
        LISTING_COLLECTION_NAME, {}) for tag in listing.get('tags', [])}

    if user_preference:
        for tag in get_current_user_data().get('preferences'):
            result[tag] = True
    elif tag_list:
        for tag in tag_list:
            result[tag] = True

    return result


def get_allergens():
    return {allergen: False for allergen in ALLERGENS}


def get_listings(query):
    return find_all(LISTING_COLLECTION_NAME, query)


def get_listing(query):
    return find(LISTING_COLLECTION_NAME, query)


def get_listing_form_data(for_db=True, image_name=None):
    form = request.form
    tags, allergens = current_tags_and_allergens()

    data = {
        'name': form.get('name'),
        'price': float(form.get('price')),
        'expiry': datetime.strptime(form.get('expiry'), '%Y-%m-%d'),
        'tags': tags,
        'allergens': allergens,
        'comments': form.get('comments').strip(),
        'address': {
            'street': form.get('street'),
            'city': form.get('city'),
            'state': form.get('state'),
            'zipcode': form.get('zipcode')
        },
    }

    if for_db:
        tags = set(form.getlist('tags'))
        tags.update(
            {tag.strip().lower() for tag in form.get('custom_tags').split(',')}
        )
        tags = list(filter(lambda tag: tag, tags))

        data['tags'] = tags
        data['user_id'] = get_current_user_data().get('_id')
        data['location'] = get_latitude_longitude(**data['address'])
        if image_name:
            data['photo'] = image_name
    else:
        data['custom_tags'] = form.get('custom_tags')

    return data


def handle_post():
    try:
        image = request.files['photo']
        timestamp = datetime.now().strftime('%Y_%m_%d_%H-%M-%S.%f')
        image_name = f'{timestamp}_{secure_filename(image.filename)}'

        # add item to db
        instance = add_listing(get_listing_form_data(image_name=image_name))
        image.save(IMAGE_DIR / image_name)
        return redirect(url_for('display_details', listing_id=instance.inserted_id))
    except Exception as e:
        return render_template(
            'food/add.html',
            item=get_listing_form_data(for_db=False),
            error=e
        )


def handle_edit(listing_id):
    try:
        if request.files['photo']:
            image = request.files['photo']
            timestamp = datetime.now().strftime('%Y_%m_%d_%H-%M-%S.%f')
            image_name = f'{timestamp}_{secure_filename(image.filename)}'
        else:
            image_name = None

        edit_listing(get_listing_form_data(image_name=image_name), listing_id)

        if image_name:
            image.save(IMAGE_DIR / image_name)

        return redirect(url_for('display_details', listing_id=listing_id))

    except Exception as e:
        return render_template(
            'food/edit.html',
            item=get_listing_form_data(for_db=False),
            error=e
        )

def get_similar_food(user_data):
    user_allergens = [ allergen for allergen in user_data['allergens'] if user_data['allergens'][allergen] ]
    user_preferences = user_data['preferences']
    similar_food = [ food for food in find_listings({'tags' : {'$in' : user_preferences}}) ]
    
    for food in similar_food:
        food_allergens = [allergen for allergen in food['allergens'] if food['allergens'][allergen]]
        for allergens in food_allergens:
            if allergens in user_allergens:
                try:
                    similar_food.remove(food)
                    break
                except:
                    pass

    return similar_food