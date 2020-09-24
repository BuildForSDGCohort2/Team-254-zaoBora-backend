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
    get_jwt_identity, get_jti, get_raw_jwt
)

from config.development import ACCESS_EXPIRES, REFRESH_EXPIRES
from app.api.v1.models.user_model import User
from app.api.v1.utils.users_validator import UserValidator

v1 = Blueprint('userv1', __name__, url_prefix='/api/v1')

# endpoint to get all users

# for key in cache.keys(): cache.delete(key)
@v1.route("/users", methods=['GET'])
def get():
    users = User().fetch_all_users()
    users_list = []

    for user in users:
        parsed_user = eval(user[0])
        user_item = {
            "username": parsed_user[0].strip(),
            "email": parsed_user[1].strip(),
            "first_name": parsed_user[2].strip(),
            "last_name": parsed_user[3].strip()
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
    revoked_store = User().redis_client

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
        validate_user.valid_farmer_bool,
        validate_user.valid_address_name
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
        "region": data['region'],
        "city": data['city'],
        "address": data['address'],
        "street_address": data['street_address'],
        "password": data['password']
    }

    reg_user = User(user_data)

    if reg_user.save_user():
        return make_response(jsonify(reg_user.save_user()), 409)
    else:
        email = user_data['email']
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        access_jti = get_jti(encoded_token=access_token)
        refresh_jti = get_jti(encoded_token=refresh_token)

        revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
        revoked_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)

        return make_response(jsonify({
            "status": 201,
            "message": "{} registered successfully".format(email),
            "username": data['username'],
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201)


# The jwt_refresh_token_required decorator insures a valid refresh
# token is present in the request before calling this endpoint. We
# can use the get_jwt_identity() function to get the identity of
# the refresh token, and use the create_access_token() function again
# to make a new access token for this identity.
@v1.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    revoked_store = User().redis_client
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    access_jti = get_jti(encoded_token=access_token)
    revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
    ret = {'access_token': access_token}

    return jsonify(ret), 201


# test protected routes
@v1.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({'hello': 'world'})


# allows registered users to login
@v1.route("/auth/login", methods=['POST'])
def login():
    data = request.get_json()
    missing_fields = UserValidator().login_fields(data)
    revoked_store = User().redis_client

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
    access_token = create_access_token(identity=credentials['email'])
    refresh_token = create_refresh_token(identity=credentials['email'])

    try:
        log_user_func['f1'] and log_user_func['f2']
        access_jti = get_jti(encoded_token=access_token)
        refresh_jti = get_jti(encoded_token=refresh_token)

        revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
        revoked_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)

        return make_response(jsonify({
            "message": "You've been successfully logged in",
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201)
    except:
        return make_response(jsonify(log_user_func), log_user_func['status'])


# endpoint allows registered users to logout
@v1.route("/auth/access_revoke/<int:userId>", methods=['DELETE'])
@jwt_required
def logout(userId):
    revoked_store = User().redis_client
    current_user_email = get_jwt_identity()

    if not User().log_out_user(current_user_email, userId):
        return jsonify({"msg": "Forbidden request!"}), 403
    else:
        jti = get_raw_jwt()['jti']
        print('==> ', revoked_store.get(jti))
        revoked_store.set(jti, 'true', ACCESS_EXPIRES * 1.2)
        return jsonify({"msg": "You've been successully logged out!"}), 200


# Endpoint for revoking the current users refresh token
@v1.route('/auth/refresh_revoke/<int:userId>', methods=['DELETE'])
@jwt_refresh_token_required
def logout2(userId):
    revoked_store = User().redis_client
    current_user_email = get_jwt_identity()

    if not User().log_out_user(current_user_email, userId):
        return jsonify({"msg": "Forbidden request!"}), 403
    else:
        jti = get_raw_jwt()['jti']
        revoked_store.set(jti, 'true', REFRESH_EXPIRES * 1.2)
        return jsonify({"msg": "Refresh token revoked"}), 200


# endpoint allows a user to update their account
@v1.route("/profile/<int:userId>", methods=['PUT', 'GET'])
@jwt_required
def update_account(userId):
    data = request.get_json()
    current_user_email = get_jwt_identity()

    if UserValidator().update_user_fields(data):
        return make_response(jsonify(UserValidator().signup_fields(data)), 400)
    else:
        validate_user = UserValidator(data)
        validation_methods = [
            validate_user.valid_update_name,
            validate_user.valid_phone_number
        ]

        for error in validation_methods:
            if error():
                return make_response(jsonify({
                    "error": error()
                }), 422)

        user_data = {
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "phone_number": data['phone_number'],
            "region": data['region'],
            "city": data['city'],
            "address": data['address'],
            "street_address": data['street_address']
        }

        update_user = User().update_user(current_user_email, user_data)

        if isinstance(update_user, dict):
            return make_response(jsonify(update_user), update_user['status'])
        else:
            return make_response(jsonify({
                "message": "Account updated successfully",
                "status": 200
            }), 200)


# endpoint allows a user to delete their account
@v1.route("/profile/<int:userId>", methods=['DELETE'])
@jwt_required
def del_account(userId):
    current_user_email = get_jwt_identity()

    remove_user = User().delete_user(current_user_email)

    if isinstance(remove_user, dict):
        return make_response(jsonify(remove_user), 404)
    else:
        return make_response(jsonify({
            "message": "User deleted successfully",
            "status": 200
        }), 200)
