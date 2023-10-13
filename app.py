from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('auth/register.html')
    
    elif request.method == 'POST':
        # do database stuff
        return redirect(url_for('index'))

@app.route('/login', methods = ['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('auth/login.html')
    
    elif request.method == 'POST':
        # do database stuff
        return redirect(url_for('index'))