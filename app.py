from flask import Flask, render_template, request, redirect, url_for, make_response, send_from_directory
from utils import (
    requires_login,
    redirect_if_logged_in,
    register_user,
    login_user,
    show_listings,
    add_listing,
    edit_profile,
    update_user_data,
    change_password,
    get_tags,
    get_allergens,
    handle_post,
    handle_edit,
    get_nearest_locations,
    get_current_location
)

from bson.objectid import ObjectId
from datetime import datetime
from db import get_current_user_data, find_all, create_index, db, insert, show_reservations, find, delete
from defaults import TEMPLATES_DIR, STATIC_DIR, LOGIN_COOKIE_NAME, IMAGE_DIR, SORT_FUNCTION_FIELDS, SORT_FUNCTION_ORDER, FILTER_FUNCTION_FIELDS, LISTING_COLLECTION_NAME, TRANSACTION_COLLECTION_NAME
from bson.objectid import ObjectId
from scripts.fill import fill


def init_app():
    app = Flask(__name__, template_folder=TEMPLATES_DIR,
                static_folder=STATIC_DIR)

    if not db[LISTING_COLLECTION_NAME].find_one():
        fill()
    create_index()

    return app


app = init_app()


@app.route('/')
def home():
    user_data = get_current_user_data()

    if not user_data:
        return render_template('index.html')
    else:
        return render_template(
            'index.html', user=user_data,
            listings=list(show_listings({'user_id': user_data['_id']})),
            reservations=list(show_reservations())
        )


@app.route('/register', methods=['GET', 'POST'])
@redirect_if_logged_in
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    elif request.method == 'POST':
        try:
            register_user(request.form)
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('auth/register.html', error=e)


@app.route('/login', methods=['GET', 'POST'])
@redirect_if_logged_in
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    elif request.method == 'POST':
        try:
            user_id, setup_complete = login_user(request.form)
            redirect_page = 'home' if setup_complete else 'profile'
            response = make_response(redirect(url_for(redirect_page)))
            response.set_cookie(LOGIN_COOKIE_NAME, str(user_id))
            return response
        except Exception as e:
            return render_template('auth/login.html', error=e)


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('home')))
    response.delete_cookie(LOGIN_COOKIE_NAME)
    return response


@app.route('/profile', methods=['GET', 'POST'])
@requires_login
def profile():
    if request.method == 'GET':
        return render_template('profile.html', user=get_current_user_data(), tags=get_tags(user_preference=True))
    elif request.method == 'POST':
        if request.form.get('update_user_data'):
            return edit_profile(request.form, update_user_data)
        elif request.form.get('change_password'):
            return edit_profile(request.form, change_password)


@app.route('/listings', methods=['GET', 'POST'])
@requires_login
def listings():
    if request.method == 'GET':
        return render_template('listings.html', listings=show_listings({}))
    elif request.method == 'POST':
        add_listing(request.form)
        return redirect(url_for('listings'))


@app.route('/listings/<listing_id>')
def display_details(listing_id):
    user_data = get_current_user_data()
    return render_template(
        'details.html',
        item=list(show_listings({'_id': ObjectId(listing_id)}))[0],
        user_id=user_data['_id'],
        reservation=find(TRANSACTION_COLLECTION_NAME, {'listing_id': ObjectId(listing_id)})
    )


@app.route('/listings/<listing_id>/edit', methods=['GET', 'POST'])
@requires_login
def edit_details(listing_id):
    item = list(show_listings({'_id': ObjectId(listing_id)}))[0]

    if get_current_user_data()['_id'] != item['user_id']:
        return redirect(url_for('listings', listing_id=listing_id))

    if (request.method == 'GET'):
        item['tags'] = get_tags(item['tags'])
        return render_template('edit.html', item=item)
    if (request.method == 'POST'):
        return handle_edit(request.form, ObjectId(listing_id))


@app.route('/listings/<listing_id>/reserve', methods=['GET'])
@requires_login
def reserve(listing_id):
    item = list(show_listings({'_id': ObjectId(listing_id)}))[0]
    if get_current_user_data()['_id'] == item['user_id'] or len(list(find_all(TRANSACTION_COLLECTION_NAME, {'listing_id': ObjectId(listing_id)}))):
        return redirect(url_for('listings', listing_id=listing_id))

    insert(
        TRANSACTION_COLLECTION_NAME,
        {
            'reserved_by': get_current_user_data()['_id'],
            'listing_id': ObjectId(listing_id),
        }
    )

    return redirect(url_for('display_details', listing_id=listing_id))


@app.route('/listings/<listing_id>/cancel', methods=['GET'])
@requires_login
def cancel(listing_id):
    delete(TRANSACTION_COLLECTION_NAME, {'listing_id': ObjectId(
        listing_id), 'reserved_by': get_current_user_data()['_id']})
    return redirect(url_for('display_details', listing_id=listing_id))


@app.route('/add', methods=['GET', 'POST'])
@requires_login
def add():
    if request.method == 'GET':
        return render_template(
            'add.html',
            item={
                'expiry': datetime.now().strftime('%Y-%m-%d'),
                'tags': get_tags(),
                'allergens': get_allergens(),
                'address': get_current_user_data()['address']
            }
        )
    elif request.method == 'POST':
        return handle_post(request.form)


@app.route('/images/<img_name>')
def serve_images(img_name):
    return send_from_directory(IMAGE_DIR, img_name)


@app.route('/search', methods=['GET'])
@requires_login
def search():
    query = request.args.get('query')
    price = request.args.get('price')
    sort = request.args.get('sortby')

    q = {}

    price_search_query = FILTER_FUNCTION_FIELDS.get(price, None)

    if price_search_query:
        q.update({'price': price_search_query})

    if query:
        q.update({"$or": [
            {'name': {'$regex': query, '$options': 'i'}},
            {'tags': {'$regex': query, '$options': 'i'}}
        ]})

    listings = show_listings(q)

    if sort:
        listings.sort(SORT_FUNCTION_FIELDS[sort], SORT_FUNCTION_ORDER[sort])

    return render_template('search.html', listings=listings)


if __name__ == '__main__':
    app.run(debug=True, port=8001)
