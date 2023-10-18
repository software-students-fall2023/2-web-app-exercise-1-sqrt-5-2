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
    show_sorted_listings
)
from datetime import datetime
from db import get_current_user_data
from defaults import TEMPLATES_DIR, STATIC_DIR, LOGIN_COOKIE_NAME, IMAGE_DIR, SORT_FUNCTION_FIELDS, SORT_FUNCTION_ORDER, FILTER_FUNCTION_FIELDS

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)


@app.route('/')
def home():
    user_data = get_current_user_data()

    if not user_data:
        return render_template('index.html')
    else:
        return render_template(
            'index.html', user=user_data, listings=list(show_listings({'user_id': user_data['_id']}))
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


@app.route('/add', methods=['GET', 'POST'])
@requires_login
def add():
    if request.method == 'GET':
        return render_template(
            'add.html',
            item={
                'quantity': 1,
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
