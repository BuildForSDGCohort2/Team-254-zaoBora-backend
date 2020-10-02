"""
This module defines all the products endpoints
"""
import json
from flask import request, jsonify, make_response, Blueprint
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, get_jti, get_raw_jwt
)

from config.development import ACCESS_EXPIRES, REFRESH_EXPIRES
from ..models.product_model import Product
from ..models.vendor_model import Vendor

v1 = Blueprint('productv1', __name__, url_prefix='/api/v1')

# endpoint to get all products
@v1.route("/products", methods=['GET'])
def get():
    products = Product().fetch_all_products('(product_name, description, quantity, regular_price, id, discounted_price, product_rating, product_review, created_on, vendor_id)', 'True = True', 'products')
    products_list = []

    # print('products are', products)

    for product in products:

        parsed_product = eval(product[0])
        # print('parsed_product is', parsed_product[0])
        # print('parsed_product is', parsed_product[1])
        # print('product is', product)
        # print ('Output==>', type(product[0]))

        username = Vendor().fetch_specific_vendor('username', f"id = {parsed_product[9]}", 'vendors')[0]
        # print('output:', username)

        product_item = {
            "product_name": parsed_product[0],
            "description": parsed_product[1],
            "quantity": parsed_product[2],
            "regular_price": parsed_product[3],
            "id": parsed_product[4],
            "discounted_price": parsed_product[5],
            "product_rating": parsed_product[6],
            "product_review": parsed_product[7],
            "created_on": parsed_product[8],
            "vendor_id": parsed_product[9],
            "vendor_name": username
        }

        # print('output',product_item)
        # res = eval(product[0])
        # print('Output Two:', product_item)
        # print ('Output====>', tuple(product[0]))
        # print ('EVAL Output<==>', res)

        products_list.append(product_item)

    return jsonify({
        "status": 200,
        "products": products_list
    }), 200

# endpoint to fetch a single product
@v1.route("/products/<int:productId>", methods=['GET'])
def get_product(productId):
    try:
        product = Product().grab_items('(product_name, description, quantity, regular_price, id, discounted_price, product_rating, product_review, created_on, vendor_id)', f'id ={productId}', 'products')
        username = Vendor().fetch_specific_vendor('username', f'id = {product[0]["f10"]}', 'vendors')[0]

        # print("Vendor Name", username)
        # print('my product is', product)
        product_item = {
            "product_name": product[0]['f1'],
            "description": product[0]['f2'],
            "quantity": product[0]['f3'],
            "regular_price": product[0]['f4'],
            "id": product[0]['f5'],
            "discounted_price": product[0]['f6'],
            "product_rating": product[0]['f7'],
            "product_review": product[0]['f8'],
            "created_on": product[0]['f9'],
            "vendor_id": product[0]['f10'],
            "vendor_name": username
        }
        # print('product item is', product_item)
        return jsonify({
            "product": product_item,
            "status": 200
        })
    except:
        return jsonify({
            "error": "product not found",
            "status": 404
        }), 404

# endpoint to create up new products
@v1.route("/<int:vendorId>/product", methods=['POST'])
@jwt_required
def create(vendorId):
    data = request.get_json()
    current_vendor_email = get_jwt_identity()

    # help with the logic  to add jwt_required breaking

    if Vendor().fetch_specific_vendor('email', f"id = {vendorId}", 'vendors'):
        # Create product
        print('all good==>', Vendor().fetch_specific_vendor('email', f"id = {vendorId}", 'vendors'))
        product_data = {
            "product_name": data['product_name'],
            "description": data['description'],
            "quantity": data['quantity'],
            "regular_price": data['regular_price'],
            "discounted_price": data['discounted_price'],
            "product_rating": data['product_rating'],
            "product_review": data['product_review'],
            "vendor_id": vendorId
            # "farmer_id": data["VENDOR" + str(random.randint(1, 999))]
        }

        reg_product = Product().save_product(current_vendor_email, product_data)

        if isinstance (reg_product, dict):
            return make_response(jsonify(reg_product), 409)
        else:
            reg_product.save_product()
            return make_response(jsonify({
                "status": 201,
                "message": "{} created successfully".format(data['product_name']),
                "product's details": {
                    "product_name": data['product_name'],
                    "description": data['description'],
                    "quantity": data['quantity'],
                    "regular_price": data['regular_price'],
                    "discounted_price": data['discounted_price'],
                    "product_rating": data['product_rating'],
                    "product_review": data['product_review'],
                    "vendor": vendorId,
                    "product_id": reg_product.fetch_product_id(data['product_name'])[0]
                    }
                }), 201)
            # else:
            # return make_response(jsonify({
            #     "error": "Please log in first!",
            #     "status": 403
            #     }), 403)
    else:
        return make_response(jsonify({
            "error": "Vendor not found or does not exist!",
            "status": 404
            }), 404)

# endpoint to update product
@v1.route("/<int:vendorId>/product/<int:productId>", methods=['PUT'])
@jwt_required
def update_product(productId, vendorId):
    data = request.get_json()

    # print(data)

    # help with the logic  to add jwt_required
    if Product().fetch_specific_product('vendor_id', f"id = {productId}", 'products')[0] == vendorId:
        # print("<<<>>>", Product().fetch_specific_product('vendor_id', f"id = {productId}", 'products')[0] == vendorId)
        product = Product().update_product(productId, data)

        if isinstance(product, dict):
            return make_response(product)
        else:
            if not Vendor().blacklisted(token):
                return make_response(jsonify({
                    "message": "product was updated successfully",
                    "status": 200
                    }), 200)
            else:
                return make_response(jsonify({
                    "error": 'please login first!',
                    "status": 403
                }), 403)
    else:
        return make_response(jsonify({
            "error": "you are not authorized to perform this action!",
            "status": 401
        }), 401)

# endpoint to delete product
@v1.route("/<int:vendorId>/product/<int:productId>", methods=['DELETE'])
@jwt_required
def delete_product(productId, vendorId):
    current_user_email = get_jwt_identity()

    if not Vendor().blacklisted(token): # help with the logic  to add jwt_required
        if Product().fetch_specific_product('vendor_id', f"id = {productId}", 'products')[0] == vendorId:
            remove_product = Product().delete_product(productId)
            if isinstance(remove_product, dict):
                return make_response(remove_product)
            else:
                return make_response(jsonify({
                    "message": f"product with id '{productId}' deleted successfully",
                    "status": 200
                    }), 200)
        else:
            return make_response(jsonify({
                "error": "you are not authorized to perform this action!",
                "status": 401
            }), 401)
    else:
        return make_response(jsonify({
            "error": 'please login first!',
            "status": 403
            }), 403)
