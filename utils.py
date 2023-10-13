from db import insert, find
from flask_bcrypt import Bcrypt


def register_user(form_data):
    first_name = form_data.get('first_name')
    last_name = form_data.get('last_name')
    email = form_data.get('email')
    password = form_data.get('password')
    password2 = form_data.get('password2')

    if password != password2:
        raise Exception('Passwords do not match!')

    password = Bcrypt().generate_password_hash(password).decode('utf-8')

    result = find('users', {'email': email})
    if result:
        raise Exception('User already exists!')

    insert(
        'users',
        {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password
        }
    )


def login_user(form_data):
    result = find('users', {'email': form_data.get('email')})
    if not result:
        raise Exception('User with that email does not exist!')

    if not Bcrypt().check_password_hash(result.get('password'), form_data.get('password')):
        raise Exception('Incorrect password!')

    return result.get('_id')
