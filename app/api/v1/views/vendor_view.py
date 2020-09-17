"""
This module defines all the vendor endpoints
"""
import re
import json 
from flask import jsonify, request, abort, make_response, json, Blueprint

# from ..models.vendor_model import Vendor, AuthenticationRequired
from ..utils.vendors_validator import VendorValidator

v1 = Blueprint('vendorv1', __name__, url_prefix='/api/v1')

# endpoint to get all vendors
@v1.route("/vendors", methods=['GET'])
def get():

    vendors = Vendor().fetch_all_vendors()
    vendors_list = []

    for vendor in vendors:
        vendors_list.append(vendor[0])

    return make_response(jsonify({
        "status": 200,
        "vendors": vendors_list
    }), 200)

# endpoint to register/sign up new vendors
@v1.route("/auth/vendor/signup", methods=['POST'])
def registration():
    
    data = request.get_json()
    
    # validate vender's input
    validate_vendor = VendorValidator(data)

    if validate_vendor.signup_fields(data):
        return make_response(jsonify(validate_vendor.signup_fields(data)), 400)
    
    validation_methods = [
        validate_vendor.valid_email,
        validate_vendor.valid_name,
        validate_vendor.validate_password,
        validate_vendor.matching_password
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
        "password": data['password']
    }

    reg_vendor = Vendor(vendor_data)

    if reg_vendor.save_vendor():
        return make_response(jsonify(reg_vendor.save_vendor()), 409)
    else:
        id = reg_vendor.fetch_vendor_id(vendor_data['username'])
        auth_token = reg_vendor.encode_auth_token(id[0])
        return make_response(jsonify({
            "status": 201,
            "message": "{} registered successfully".format(data['email']),
            "username": data['username'],
            "auth_token": auth_token.decode('utf-8')
        }), 201)        
            
# endpoint to login/signin vendor # allows registered vendors to login
@v1.route("/auth/vendor/login", methods=['POST'])
def login():
   data = request.get_json()
   missing_fields = VendorValidator().login_fields(data)

   if missing_fields:
      return make_response(jsonify(missing_fields), 400)

   validate_vendor = VendorValidator(data)
   reg_email = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")

   if not re.match(reg_email, str(data['email'])):
       return make_response(jsonify({
           "error": validate_vendor.valid_email()
       }), 422)

   credentials = {
       "email": data['email'],
       "password": data['password']
   }

   log_vendor = Vendor().log_in_vendor(credentials)
   try:
       log_vendor['f1'] and log_vendor['f2']
       auth_token = Vendor().encode_auth_token(log_vendor['f1'])
       store = {
            "token": auth_token.decode('utf-8'),
            "email": credentials['email']
        }
       return make_response(jsonify({
            "status": 201,
            "message": "{} has been successfully logged in".format(data['email']),
            "auth_token": auth_token.decode('utf-8'),
            "id": log_vendor['f1'],
            "username": log_vendor['f2']
        }), 201)
   except:
       return make_response(jsonify(log_vendor), log_vendor['status'])

# endpoint allows registered vendors to logout
@v1.route("/auth/vendor/<int:vendorId>/logout", methods=['POST'])
# @AuthenticationRequired
def logout(vendorId):
    auth_token = request.headers.get('Authorization')
    token = auth_token.split(" ")[1]
    print(token)

    if Vendor().log_out_vendor(vendorId) == False:
        return make_response(jsonify({
            "error": "Vendor does not exist!",
            "status": 404
        }), 404)
    else:
        username = Vendor().log_out_vendor(vendorId)

        det = dict(
            username=username,
            token=token
        )

        values = tuple(det.values())

        if Vendor().blacklisted(token):
            return make_response(jsonify({
                "error": "Token is blacklisted",
                "status": 400
            }), 400)
        else:
            Vendor().blacklist(values)
            return make_response(jsonify({
                "message": "You have been logged out",
                "status": 200
            }), 200)

# endpoint allows a vendor to delete their account

# endpoint allows a vendor to update their account
@v1.route("/profile/vendor/<int:vendorId>", methods=['PUT', 'GET'])
# @AuthenticationRequiredc
def update_account(vendorId):
    auth_token = request.headers.get('Authorization')
    token = auth_token.split(" ")[1]

    if request.method == 'PUT':
        data = request.get_json()
        if VendorValidator().signup_fields(data):
            return make_response(jsonify(VendorValidator().signup_fields(data)), 400)
        else:
            # Validate vendor
            validate_vendor = VendorValidator(data)
            validation_methods = [
                validate_vendor.valid_email,
                validate_vendor.valid_name,
                validate_vendor.validate_password,
                validate_vendor.matching_password
            ]

            for error in validation_methods:
                if error():
                    return make_response(jsonify({
                        "error": error()
                    }), 422)
                    
        vendor_data = {
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "email": data['email'],
            "username": data['username'],
            "password": data['password'],
        }    

        update_vendor = Vendor().update_vendor(vendorId, vendor_data)
        
        if isinstance(update_vendor, dict):
            print('==>>', update_vendor)
            return make_response(jsonify(update_vendor), update_vendor['status'])
        elif Vendor().blacklisted(token):
            return make_response(jsonify({
                "error": "Please log in first!"
            }), 400)
        else:
            return make_response(jsonify({
                "message": f"user {vendor_data['email']} updated successfully",
                "status": 200
            }), 200) 
        # get updated vendor data
    