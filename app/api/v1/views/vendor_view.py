"""
This module defines all the user endpoints
"""
import re
import json
import requests
from flask import jsonify, request, abort, make_response, json, Blueprint, url_for
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, get_jti, get_raw_jwt
)

from config.development import ACCESS_EXPIRES, REFRESH_EXPIRES
from app.api.v1.models.vendor_model import Vendor
from app.api.v1.models.user_model import User
from app.api.v1.utils.users_validator import UserValidator
from app.api.v1.utils.email import send_email, generate_verification_token, confirm_verification_token

v1 = Blueprint('vendorv1', __name__, url_prefix='/api/v1')

# endpoint to get all vendors

# for key in cache.keys(): cache.delete(key)
@v1.route("/vendors", methods=['GET'])
def get():
    vendors = Vendor().fetch_all_vendors()
    vendors_list = []

    for vendor in vendors:
        parsed_vendor = eval(vendor[0])
        vendor_item = {
            "username": parsed_vendor[0].strip(),
            "email": parsed_vendor[1].strip(),
            "first_name": parsed_vendor[2].strip(),
            "last_name": parsed_vendor[3].strip()
        }

        vendors_list.append(vendor_item)

    return make_response(jsonify({
        "status": 200,
        "vendors": vendors_list
    }), 200)


# endpoint to register/sign up new vendors
@v1.route("/vendor/auth/signup", methods=['POST'])
def registration():
    data = request.get_json()
    revoked_store = Vendor().redis_client

    # validate vendor's input
    validate_vendor = UserValidator(data)

    if validate_vendor.vendor_signup_fields(data):
        return jsonify(validate_vendor.vendor_signup_fields(data)), 400

    validation_methods = [
        validate_vendor.valid_email,
        validate_vendor.valid_name,
        validate_vendor.validate_password,
        validate_vendor.matching_password,
        validate_vendor.valid_phone_number,
        validate_vendor.valid_address_name
    ]

    for error in validation_methods:
        if error():
            return make_response(jsonify({
                "error": error(),
                "status": 422
            }), 422)

    # Register vendor
    vendor_data = {
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "email": data['email'],
        "username": data['username'],
        "phone_number": data['phone_number'],
        "region": data['region'],
        "city": data['city'],
        "address": data['address'],
        "street_address": data['street_address'],
        "password": data['password']
    }

    reg_vendor = Vendor(vendor_data)

    if reg_vendor.save_vendor():
        return make_response(jsonify(reg_vendor.save_vendor()), 409)
    else:
        email = vendor_data['email']
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
            'vendorv1.confirm_vendor_email', token=token, _external=True)
        print('link ==> ',verification_email)
        send_mail_res = send_email(email, tokens, verification_email)

    return jsonify(send_mail_res), send_mail_res['status']


# allows registered vendors to login
@v1.route("/vendor/auth/login", methods=['POST'])
def login():
    data = request.get_json()
    missing_fields = UserValidator().login_fields(data)
    revoked_store = Vendor().redis_client

    if missing_fields:
        return make_response(jsonify(missing_fields), 400)

    validate_vendor = UserValidator(data)
    reg_email = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")

    if not re.match(reg_email, str(data['email'])):
        return make_response(jsonify({
            "error": validate_vendor.valid_email()
        }), 422)

    credentials = {
        "email": data['email'],
        "password": data['password']
    }

    vendor = Vendor().log_in_vendor(credentials)
    access_token = create_access_token(identity=credentials['email'])
    refresh_token = create_refresh_token(identity=credentials['email'])

    try:
        vendor['status']
        return make_response(jsonify(vendor), vendor['status'])
    except:
        email = vendor['email']
        access_jti = get_jti(encoded_token=access_token)
        refresh_jti = get_jti(encoded_token=refresh_token)

        revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
        revoked_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)

        if not vendor['email_confirmed']:        
            token = generate_verification_token(email)
            verification_email = url_for(
                'userv1.confirm_email', token=token, _external=True)
            tokens = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "username": vendor['username']
            }
            send_mail_res = send_email(email, tokens, verification_email)

            return jsonify(send_mail_res), send_mail_res['status']
        else:
            return make_response(jsonify({
                "message": "You've been successfully logged in",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "authenticated": True,
                "vendor": vendor
            }), 201)


# # endpoint allows registered vendors to logout
# @v1.route("/vendor/auth/access_revoke/<int:vendorId>", methods=['DELETE'])
# @jwt_required
# def logout(vendorId):
#     revoked_store = Vendor().redis_client
#     current_vendor_email = get_jwt_identity()

#     if not Vendor().log_out_vendor(current_vendor_email, vendorId):
#         return jsonify({"msg": "Forbidden request!"}), 403
#     else:
#         jti = get_raw_jwt()['jti']
        
#         revoked_store.set(jti, 'true', ACCESS_EXPIRES * 1.2)
#         return jsonify({"msg": "You've been successully logged out!"}), 200


# # Endpoint for revoking the current vendors refresh token
# @v1.route('/vendor/auth/refresh_revoke/<int:vendorId>', methods=['DELETE'])
# @jwt_refresh_token_required
# def logout2(vendorId):
#     revoked_store = Vendor().redis_client
#     current_vendor_email = get_jwt_identity()

#     if not Vendor().log_out_vendor(current_vendor_email, vendorId):
#         return jsonify({"msg": "Forbidden request!"}), 403
#     else:
#         jti = get_raw_jwt()['jti']
#         revoked_store.set(jti, 'true', REFRESH_EXPIRES * 1.2)
#         return jsonify({"msg": "Refresh token revoked"}), 200


# endpoint allows a vendor to update their account
@v1.route("/vendor/profile/<int:vendorId>", methods=['PUT', 'GET'])
@jwt_required
def update_account(vendorId):
    data = request.get_json()
    current_vendor_email = get_jwt_identity()

    if UserValidator().update_user_fields(data):
        return make_response(jsonify(UserValidator().signup_fields(data)), 400)
    else:
        validate_vendor = UserValidator(data)
        validation_methods = [
            validate_vendor.valid_update_name,
            validate_vendor.valid_phone_number
        ]

        for error in validation_methods:
            if error():
                return make_response(jsonify({
                    "error": error()
                }), 422)

        vendor_data = {
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "phone_number": data['phone_number'],
            "region": data['region'],
            "city": data['city'],
            "address": data['address'],
            "street_address": data['street_address']
        }

        update_vendor = Vendor().update_vendor(current_vendor_email, vendor_data)

        if isinstance(update_vendor, dict):
            return make_response(jsonify(update_vendor), update_vendor['status'])
        else:
            return make_response(jsonify({
                "message": "Account updated successfully",
                "status": 200
            }), 200)


# endpoint allows a vendor to delete their account
@v1.route("/vendor/profile/<int:vendorId>", methods=['DELETE'])
@jwt_required
def del_account(vendorId):
    current_vendor_email = get_jwt_identity()

    remove_vendor = Vendor().delete_vendor(current_vendor_email)

    if isinstance(remove_vendor, dict):
        return make_response(jsonify(remove_vendor), 404)
    else:
        return make_response(jsonify({
            "message": "Vendor deleted successfully",
            "status": 200
        }), 200)


@v1.route('/confirm-vendor-email/<token>')
def confirm_vendor_email(token):
    email = confirm_verification_token(token)

    if isinstance(email, str):
        try:
            vendor = Vendor().fetch_specific_vendor(
                'email',
                f"email = '{email}'",
                'vendors'
            )
        except Exception as e:
            print(e)
            return jsonify({
                "error": "Error processing request"
            }), 400

        if not vendor:
            print('vendor --> ',vendor)
            return jsonify({
                "error": "Error fetching email"
            }), 422
        else:
            User().verify_email(email, 'vendors')
            return jsonify({
                "msg": "Email verified successfully"
            }), 200
    else:
        return jsonify(email), email['status']
