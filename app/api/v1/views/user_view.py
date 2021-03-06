"""
This module defines all the user endpoints
"""
import re
import json
import requests
from flask import (
    jsonify, request, abort, make_response, json, Blueprint, render_template_string, url_for, redirect)
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, get_jti, get_raw_jwt
)
from flask_mail import Message
from itsdangerous import (
    URLSafeTimedSerializer, SignatureExpired, BadTimeSignature)
from flask import current_app
from flask_cors import cross_origin

from config.development import (
    ACCESS_EXPIRES, REFRESH_EXPIRES, SECURITY_PASSWORD_SALT, SECRET_KEY)
from app.api.v1.models.user_model import User
from app.api.v1.models.vendor_model import Vendor
from app.api.v1.utils.users_validator import UserValidator
from app.api.v1.utils.email import send_email, confirm_verification_token, generate_verification_token

v1 = Blueprint('userv1', __name__, url_prefix='/api/v1')
serializer = URLSafeTimedSerializer(SECRET_KEY)
DEV_BASE_URL = 'http://localhost:8080/#/'
BASE_URL = 'https://buildforsdgcohort2.github.io/Team-254-zaoBora-frontend/#/'

# for key in cache.keys(): cache.delete(key)

# endpoint to get all users


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


# Fetch active user
@v1.route("/<string:account>/active", methods=['GET'])
@jwt_required
def fetch_active_user(account):
    accounts = ['user', 'vendor']

    if not account in accounts:
        return jsonify({
            "error": "Invalid account type! (user/vendor)"    
        }), 422

    account_type = User() if account == 'user' else Vendor()
    revoked_store = account_type.redis_client
    try:
        active_user_email = get_jwt_identity()
        userDetails = account_type.fetch_specific_user(
            'first_name, last_name, username, phone_number, email, city, region, address, street_address, is_farmer',
            f"email = '{active_user_email}'",
            'users'
        ) if account == 'user' else account_type.fetch_specific_vendor(
            'first_name, last_name, username, phone_number, email, city, region, address, street_address, is_farmer',
            f"email = '{active_user_email}'",
            'users'
        )
        user = {
            "first_name": userDetails[0].strip(),
            "last_name": userDetails[1].strip(),
            "username": userDetails[2].strip(),
            "phone_number": userDetails[3].strip(),
            "email": userDetails[4].strip(),
            "city": userDetails[5].strip(),
            "region": userDetails[6].strip(),
            "address": userDetails[7].strip(),
            "street_address": userDetails[8].strip(),
            "is_farmer": userDetails[9]
        }

        access_token = create_access_token(identity=active_user_email)
        refresh_token = create_refresh_token(identity=active_user_email)
        access_jti = get_jti(encoded_token=access_token)
        refresh_jti = get_jti(encoded_token=refresh_token)

        print('---------')
        try:
            revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
            revoked_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)
        except Exception as e:
            print('--> ',e)

        return jsonify({
            'user': user,
            'authenticated': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'account': account
        }), 200
    except:
        return jsonify({'msg': f'{account} not found!'}), 404


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

        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "username": data['username']
        }

        token = generate_verification_token(email)
        verification_email = url_for(
            'userv1.confirm_email', token=token, _external=True)
        send_mail_res = send_email(email, tokens, verification_email)

        return jsonify(send_mail_res), send_mail_res['status']


# Confirm email endpoint
@v1.route('/confirm-email/<token>')
def confirm_email(token):
    email = confirm_verification_token(token)

    if isinstance(email, str):
        try:
            user = User().fetch_specific_user(
                'email',
                f"email = '{email}'",
                'users'
            )
        except Exception as e:
            print(e)
            return jsonify({
                "error": "Error processing request"
            }), 400

        if not user:
            return jsonify({
                "error": "Error fetching email"
            }), 422
        else:
            verify = User().verify_email(email, 'users')
            try:
                verify == 'verified'
                return redirect(f"{DEV_BASE_URL}email-verified", code=302)
            except:
                return jsonify({
                    "error": "Email verification failed"
                }), 400
    else:
        return jsonify(email), email['status']


# Resend email endpoint
@v1.route('/<string:acc_type>/resend-email', methods=['POST'])
@jwt_required
def resend_email(acc_type):
    auth_user_email = get_jwt_identity()
    data = request.get_json()
    email = data['email']
    users = acc_type == "users"
    vendors = acc_type == "vendors"

    dup_email = User().fetch_specific_user(
        'email',
        f"email = '{email}'",
        acc_type
    )

    if (not dup_email) or (email == auth_user_email):
        try:
            users or vendors
            token = generate_verification_token(email)
            verification_email = url_for(
                'userv1.confirm_email', token=token, _external=True)
            send_mail_res = send_email(email, {}, verification_email)
        except:
            return jsonify({
                "error": "Error processing request"    
            }), 400
    else:
        return jsonify({
            "error": "This email already exists"
        }), 422

    return jsonify(send_mail_res), send_mail_res['status']


# The jwt_refresh_token_required decorator insures a valid refresh
# token is present in the request before calling this endpoint. We
# can use the get_jwt_identity() function to get the identity of
# the refresh token, and use the create_access_token() function again
# to make a new access token for this identity.

# Refresh token endpoint
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
    print('------------------------------------------------')
    print('----> ',data)
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

    user = User().log_in_user(credentials)
    access_token = create_access_token(identity=credentials['email'])
    refresh_token = create_refresh_token(identity=credentials['email'])
    print('------------------------------------------------')
    print('----> ',user)

    if 'status' in user:
        return make_response(jsonify(user), user['status'])
    else:
        print('>>>>>> ',user)
        email = user['email']
        access_jti = get_jti(encoded_token=access_token)
        refresh_jti = get_jti(encoded_token=refresh_token)
        print('------------------------------------------------')
        print('access_token: ',access_token)
        print('refresh_token: ',refresh_token)
        print('access_jti: ',access_jti)
        print('refresh_jti: ',refresh_jti)
        print('revoked_store: ', revoked_store)
        print('------------------------------------------------')

        revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
        revoked_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)
        print('================================================')

        if not user['email_confirmed']:    
            token = generate_verification_token(email)
            verification_email = url_for(
                'userv1.confirm_email', token=token, _external=True)
            tokens = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "username": user['username']
            }
            send_mail_res = send_email(email, tokens, verification_email)

            return jsonify(send_mail_res), send_mail_res['status']
        else:
            return jsonify({
                "message": "You've been successfully logged in",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "authenticated": True,
                "user": user
            }), 201


# endpoint allows registered users to logout
@v1.route("/auth/access_revoke/<string:account>/<string:userEmail>", methods=['DELETE'])
@jwt_required
def logout(account, userEmail):
    account = User() if type == 'user' else Vendor()
    revoked_store = account.redis_client
    auth_user_email = get_jwt_identity()

    if auth_user_email != userEmail:
        return jsonify({"msg": "Forbidden request!"}), 403
    else:
        jti = get_raw_jwt()['jti']
        print('==> ', revoked_store.get(jti))
        revoked_store.set(jti, 'true', ACCESS_EXPIRES * 1.2)
        return jsonify({"msg": "You've been successully logged out!"}), 200


# Endpoint for revoking the current users refresh token
@v1.route('/auth/refresh_revoke/<string:account>/<string:userEmail>', methods=['DELETE'])
@jwt_refresh_token_required
def logout2(account, userEmail):
    account = User() if type == 'user' else Vendor()
    revoked_store = account.redis_client
    auth_user_email = get_jwt_identity()

    if auth_user_email != userEmail:
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
