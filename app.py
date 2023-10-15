from flask import Flask, render_template, request, redirect, url_for, make_response
from utils import register_user, login_user, show_listings, requires_login
from db import get_current_user_data
from defaults import TEMPLATES_DIR, STATIC_DIR, LOGIN_COOKIE_NAME

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)


@app.route('/')
def home():
    return render_template('index.html', user=get_current_user_data())


@app.route('/register', methods=['GET', 'POST'])
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
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    elif request.method == 'POST':
        try:
            user_id = login_user(request.form)
            response = make_response(redirect(url_for('home')))
            response.set_cookie(LOGIN_COOKIE_NAME, str(user_id))
            return response
        except Exception as e:
            return render_template('auth/login.html', error=e)


@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('home')))
    response.delete_cookie(LOGIN_COOKIE_NAME)
    return response


@app.route('/listings', methods=['GET', 'POST'])
@requires_login
def listings():
    if request.method == 'GET':
        return render_template('listings.html', listings_array=show_listings({}))

@app.route('/additems', methods = ['GET'])
@requires_login
def additems():
    return render_template('additems.html')