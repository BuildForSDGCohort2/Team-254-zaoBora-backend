"""
This module defines all the user endpoints
"""
import re
import json
import requests
from flask import jsonify, request, abort, make_response, json, Blueprint
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)

from ..models.user_model import User, AuthenticationRequired
from ..utils.users_validator import UserValidator
from ..utils import transact_mpesa

v1 = Blueprint('userv1', __name__, url_prefix='/api/v1')

# endpoint to get all users


@v1.route("/users", methods=['GET'])
def get():

    users = User().fetch_all_users()
    users_list = []

    for user in users:
        parsed_user = eval(user[0])
        user_item = {
            "username": parsed_user[0].strip(),
            "email": parsed_user[1].strip()
        }

        users_list.append(user_item)

    return make_response(jsonify({
        "status": 200,
        "users": users_list
    }), 200)

# endpoint to register/sign up new users


@v1.route("/auth/signup", methods=['POST'])
def registration():
    data = request.get_json()

    # validate user's input
    validate_user = UserValidator(data)

    if validate_user.signup_fields(data):
        return make_response(jsonify(validate_user.signup_fields(data)), 400)

    validation_methods = [
        validate_user.valid_email,
        validate_user.valid_name,
        validate_user.validate_password,
        validate_user.matching_password,
        validate_user.valid_phone_number,
        validate_user.valid_farmer_bool
    ]

    for error in validation_methods:
        if error():
            return make_response(jsonify({
                "error": error(),
                "status": 422
            }), 422)

    # Register user
    user_data = {
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "email": data['email'],
        "username": data['username'],
        "phone_number": data['phone_number'],
        "is_farmer": data['is_farmer'],
        "password": data['password']
    }

    reg_user = User(user_data)
    
    if reg_user.save_user():
        return make_response(jsonify(reg_user.save_user()), 409)
    else:
        email = user_data['email']

        return make_response(jsonify({
            "status": 201,
            "message": "{} registered successfully".format(email),
            "username": data['username'],
            "access_token": create_access_token(identity=email),
            "refresh_token": create_refresh_token(identity=email)
        }), 201)

# The jwt_refresh_token_required decorator insures a valid refresh
# token is present in the request before calling this endpoint. We
# can use the get_jwt_identity() function to get the identity of
# the refresh token, and use the create_access_token() function again
# to make a new access token for this identity.


@v1.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200


# Example
# @v1.route('/protected', methods=['GET'])
# @jwt_required
# def protected():
#     username = get_jwt_identity()
#     return jsonify(logged_in_as=username), 200

# allows registered users to login


@v1.route("/auth/login", methods=['POST'])
@jwt_required
def login():
    data = request.get_json()
    missing_fields = UserValidator().login_fields(data)

    if missing_fields:
        return make_response(jsonify(missing_fields), 400)

    validate_user = UserValidator(data)
    reg_email = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")

    if not re.match(reg_email, str(data['email'])):
        return make_response(jsonify({
            "error": validate_user.valid_email()
        }), 422)

    credentials = {
        "email": data['email'],
        "password": data['password']
    }

    log_user_func = User().log_in_user(credentials)
    
    try:
        log_user_func['f1'] and log_user_func['f2']
        decoded_token = get_jwt_identity()

        if decoded_token == data['email']:
            return make_response(jsonify({
                "message": "You've been successfully logged in",
                "access_token": create_access_token(identity=credentials['email']),
                "refresh_token": create_refresh_token(identity=credentials['email'])
            }), 201)
    except:
        return make_response(jsonify(log_user_func), log_user_func['status'])

# endpoint allows registered users to logout


@v1.route("/auth/<int:userId>/logout", methods=['POST'])
@AuthenticationRequired
def logout(userId):
    auth_token = request.headers.get('Authorization')
    token = auth_token.split(" ")[1]
    print(token)

    if User().log_out_user(userId) == False:
        return make_response(jsonify({
            "error": "User does not exist!",
            "status": 404
        }), 404)
    else:
        username = User().log_out_user(userId)

        det = dict(
            username=username,
            token=token
        )

        values = tuple(det.values())

        if User().blacklisted(token):
            return make_response(jsonify({
                "error": "Token is blacklisted",
                "status": 400
            }), 400)
        else:
            User().blacklist(values)
            return make_response(jsonify({
                "message": "You have been logged out",
                "status": 200
            }), 200)

# endpoint allows a user to delete their account


@v1.route("/profile/<int:userId>", methods=['DELETE'])
@AuthenticationRequired
def del_account(userId):
    auth_token = request.headers.get('Authorization')
    token = auth_token.split(" ")[1]

    remove_user = User().delete_user(userId)

    if isinstance(remove_user, dict):
        return make_response(jsonify(remove_user), 404)
    elif User().blacklisted(token):
        return make_response(jsonify({
            "error": "Please log in first!"
        }), 400)
    elif not User().blacklisted(token):
        return make_response(jsonify({
            "message": f"user with id '{userId}' deleted successfully",
            "status": 200
        }), 200)

# endpoint allows a user to update their account


@v1.route("/profile/<int:userId>", methods=['PUT', 'GET'])
@AuthenticationRequired
def update_account(userId):
    auth_token = request.headers.get('Authorization')
    token = auth_token.split(" ")[1]

    if request.method == 'PUT':
        data = request.get_json()
        if UserValidator().signup_fields(data):
            return make_response(jsonify(UserValidator().signup_fields(data)), 400)
        else:
            # Validate user
            validate_user = UserValidator(data)
            validation_methods = [
                validate_user.valid_email,
                validate_user.valid_name,
                validate_user.validate_password,
                validate_user.matching_password
            ]

            for error in validation_methods:
                if error():
                    return make_response(jsonify({
                        "error": error()
                    }), 422)

        user_data = {
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "email": data['email'],
            "username": data['username'],
            "password": data['password'],
        }

        update_user = User().update_user(userId, user_data)

        if isinstance(update_user, dict):
            print('==>>', update_user)
            return make_response(jsonify(update_user), update_user['status'])
        elif User().blacklisted(token):
            return make_response(jsonify({
                "error": "Please log in first!"
            }), 400)
        else:
            return make_response(jsonify({
                "message": f"user {user_data['email']} updated successfully",
                "status": 200
            }), 200)
        # get updated user data


@v1.route("/lipa_mpesa")
def lipa():
    pay_online = transact_mpesa.lipa_na_mpesa()
    return pay_online
