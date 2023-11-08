from flask import Flask, render_template, request, redirect, url_for, make_response, send_from_directory
from utils import (
    requires_login,
    redirect_if_logged_in,
    register_user,
    login_user,
    get_listings,
    add_listing,
    edit_profile,
    update_user_data,
    change_password,
    get_tags,
    get_allergens,
    handle_post,
    handle_edit,
    get_listing,
    get_similar_food
)
from bson.objectid import ObjectId
from datetime import datetime
from db import (
    get_user_data,
    get_current_user_data,
    find_listings,
    create_index,
    db,
    insert,
    show_reservations,
    find,
    find_all,
    delete,
    delete_all
)
from defaults import (
    TEMPLATES_DIR,
    STATIC_DIR,
    LOGIN_COOKIE_NAME,
    IMAGE_DIR,
    SORT_FUNCTION_FIELDS,
    SORT_FUNCTION_ORDER,
    FILTER_FUNCTION_FIELDS,
    LISTING_COLLECTION_NAME,
    TRANSACTION_COLLECTION_NAME
)
from bson.objectid import ObjectId
from scripts.fill import fill as fill_dummy_data


def init_app():
    app = Flask(
        __name__,
        template_folder=TEMPLATES_DIR,
        static_folder=STATIC_DIR
    )

    # if database is empty, fill it with dummy data
    if not db[LISTING_COLLECTION_NAME].find_one():
        fill_dummy_data()

    # create index for different fields in the collections
    create_index()

    return app


app = init_app()


@app.route('/')
def home():
    user_data = get_current_user_data()

    if not user_data:
        return render_template('index.html')
    else:
        food_near_user = None
        if user_data['location']['coordinates'] != [0, 0]:
            food_near_user = find_listings({'user_id': {'$ne': user_data['_id']}}, {'distance': 1})[:4]
        return render_template(
            'index.html',
            user=user_data,
            listings=find_listings({'user_id': user_data['_id']}),
            reservations=list(show_reservations()),
            near=food_near_user,
            recommended=get_similar_food(user_data)
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
            return render_template(
                'auth/register.html',
                error=e,
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                email=request.form.get('email')
            )


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
            return render_template('auth/login.html', error=e, email=request.form.get('email'))


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


@app.route('/profile/delete', methods=['GET'])
@requires_login
def delete_profile():
    user_id = get_current_user_data()['_id']
    listings_ids = [listing['_id'] for listing in find_all(LISTING_COLLECTION_NAME, {'user_id': user_id})]

    delete_all(TRANSACTION_COLLECTION_NAME, {'reserved_by': user_id})
    delete_all(TRANSACTION_COLLECTION_NAME, {'listing_id': {'$in': listings_ids}})
    delete_all(LISTING_COLLECTION_NAME, {'user_id': user_id})
    delete('users', {'_id': user_id})
    return redirect(url_for('logout'))


@app.route('/listings', methods=['GET', 'POST'])
@requires_login
def listings():
    if request.method == 'GET':
        return render_template('food/listings.html',
                               listings=find_listings({}),
                               user_id=get_current_user_data()['_id'])

    elif request.method == 'POST':
        add_listing(request.form)
        return redirect(url_for('listings'))


@app.route('/listings/<listing_id>')
@requires_login
def display_details(listing_id):
    item = get_listing({'_id': ObjectId(listing_id)})
    if not item:
        return redirect(url_for('listings'))

    reservation = find(
        TRANSACTION_COLLECTION_NAME,
        {'listing_id': ObjectId(listing_id)}
    )

    user_data = get_current_user_data()
    poster_data = get_user_data(user_id=item['user_id'])
    reserver_data = get_user_data(
        user_id=reservation['reserved_by']) if reservation else None

    # get food that have the same tags as the current food.
    similar_food = [food for food in get_listings({'tags': {'$in': item['tags']}})
                    if food['_id'] != ObjectId(listing_id)]

    allergens_overlap = []
    for allergen in user_data['allergens']:
        if user_data['allergens'][allergen] and item['allergens'][allergen]:
            allergens_overlap.append(allergen)

    return render_template(
        'food/details.html',
        item=item,
        user_id=user_data['_id'],
        reservation=reservation,
        similar_food=similar_food,
        poster=poster_data,
        reserver=reserver_data,
        allergens_warning=allergens_overlap,
    )


@app.route('/listings/<listing_id>/edit', methods=['GET', 'POST'])
@requires_login
def edit_details(listing_id):
    item = get_listing({'_id': ObjectId(listing_id)})
    if not item:
        return redirect(url_for('listings'))

    if get_current_user_data()['_id'] != item['user_id']:
        return redirect(url_for('listings', listing_id=listing_id))

    if (request.method == 'GET'):
        item['tags'] = get_tags(tag_list=item['tags'])
        return render_template('food/edit.html', item=item)

    elif (request.method == 'POST'):
        return handle_edit(listing_id=ObjectId(listing_id))


@app.route('/listings/<listing_id>/reserve', methods=['GET'])
@requires_login
def reserve(listing_id):
    item = get_listing({'_id': ObjectId(listing_id)})

    # user cannot reserve their own food or reserve food that is already reserved
    if get_current_user_data()['_id'] == item['user_id'] or find(TRANSACTION_COLLECTION_NAME, {'listing_id': ObjectId(listing_id)}):
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
    delete(TRANSACTION_COLLECTION_NAME, {
        'listing_id': ObjectId(listing_id),
        'reserved_by': get_current_user_data()['_id']
    })
    return redirect(url_for('display_details', listing_id=listing_id))


@app.route('/listings/<listing_id>/delete', methods=['GET'])
@requires_login
def delete_listing(listing_id):
    item = get_listing({'_id': ObjectId(listing_id)})
    if not item:
        return redirect(url_for('listings'))

    if get_current_user_data()['_id'] != item['user_id']:
        return redirect(url_for('listings', listing_id=listing_id))

    delete(TRANSACTION_COLLECTION_NAME, {'listing_id': ObjectId(listing_id)})
    delete(LISTING_COLLECTION_NAME, {'_id': ObjectId(listing_id)})

    return redirect(url_for('listings'))


@app.route('/add', methods=['GET', 'POST'])
@requires_login
def add():
    if request.method == 'GET':
        return render_template(
            'food/add.html',
            item={
                'expiry': datetime.now(),
                'tags': get_tags(),
                'allergens': get_allergens(),
                'address': get_current_user_data()['address']
            }
        )
    elif request.method == 'POST':
        return handle_post()


@app.route('/images/<img_name>')
def serve_images(img_name):
    return send_from_directory(IMAGE_DIR, img_name)


@app.route('/search', methods=['GET'])
@requires_login
def search():
    query = request.args.get('query')
    price = request.args.get('price')
    sort = request.args.get('sortby')
    exclude_allergens = request.args.get('exclude_allergens') == 'on'

    q = {}

    price_search_query = FILTER_FUNCTION_FIELDS.get(price, None)
    if price_search_query:
        q.update({'price': price_search_query})

    if query:
        q.update({"$or": [
            {'name': {'$regex': query, '$options': 'i'}},
            {'tags': {'$regex': query, '$options': 'i'}}
        ]})

    if exclude_allergens:
        allergens = get_current_user_data()['allergens']
        for allergen in allergens:
            if allergens[allergen]:
                q.update({f'allergens.{allergen}': {'$ne': True}})

    if sort:
        listings = find_listings(
            match_query=q,
            sort_query={SORT_FUNCTION_FIELDS[sort]: SORT_FUNCTION_ORDER[sort]}
        )
    else:
        listings = find_listings(q)

    return render_template('food/search.html', listings=listings, price=price, sort=sort, query=query or '', exclude_allergens=exclude_allergens)


@app.template_filter('filter_date')
def filter_date(date):
    return date.strftime('%B %d, %Y')


@app.template_filter('any')
def if_any(values):
    return any(values)


if __name__ == '__main__':
    app.run(debug=True, port=8001)
