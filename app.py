from flask import Flask, render_template, request, redirect, url_for, make_response
from dotenv import load_dotenv
from utils import register_user, login_user, show_listings

load_dotenv()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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
            response = make_response(redirect(url_for('index')))
            response.set_cookie('session_id', str(user_id))
            return response
        except Exception as e:
            return render_template('auth/login.html', error=e)

@app.route('/listings', methods = ['GET', 'POST'])
def listings():
    if request.method == 'GET':
        return render_template('listings.html', listings_array = show_listings({}))
