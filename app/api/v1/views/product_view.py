"""
This module defines all the products endpoints
"""
import json
import uuid
from flask import request, jsonify, make_response, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api.v1.models.product_model import Product
from app.api.v1.models.vendor_model import Vendor
from app.api.v1.models.user_model import User

v1 = Blueprint('productv1', __name__, url_prefix='/api/v1')


# endpoint to get all products
@v1.route("/products", methods=['GET'])
def get():
    products = Product().fetch_all_products(
        '(vendor_id, product_name, product_id, description, quantity, regular_price, discounted_price, product_rating, mass, created_on)',
        'True = True', 'products')
    products_list = []

    for product in products:
        parsed_product = eval(product[0])
        username = Vendor().fetch_specific_vendor(
            'username', f"id = {parsed_product[0]}", 'vendors')[0]

        product_item = {
            "vendor_name": username.strip(),
            "product_name": parsed_product[1],
            "product_id": parsed_product[2],
            "description": parsed_product[3],
            "quantity": parsed_product[4],
            "regular_price": parsed_product[5],
            "discounted_price": parsed_product[6],
            "product_rating": parsed_product[7],
            "mass": parsed_product[8].strip(),
            "created_on": parsed_product[9]
        }

        products_list.append(product_item)

    return jsonify({
        "status": 200,
        "products": products_list
    }), 200


# endpoint to fetch a single product
@v1.route("/products/<string:productId>", methods=['GET'])
def get_product(productId):
    product = Product().grab_items(
        '(vendor_id, product_name, product_id, description, quantity, regular_price, discounted_price, product_rating, mass, created_on)',
        f"product_id ='{productId}'",
        'products')
    
    if not product:
        return jsonify({
            "error": "Product not found!"
        }), 404
        
    product_tuple = product[0]
    username = Vendor().fetch_specific_vendor(
        'username', f"id = '{product_tuple['f1']}'", 'vendors')[0]
    product_item = {
        "vendor_name": username.strip(),
        "product_name": product_tuple['f2'],
        "product_id": product_tuple['f3'].strip(),
        "description": product_tuple['f4'],
        "quantity": product_tuple['f5'],
        "regular_price": product_tuple['f6'],
        "discounted_price": product_tuple['f7'],
        "product_rating": product_tuple['f8'],
        "mass": product_tuple['f9'].strip(),
        "created_on": product_tuple['f10']
    }

    return jsonify({
        "product": product_item,
        "status": 200
    })


# endpoint to create new products
@v1.route("/product/create", methods=['POST'])
@jwt_required
def create():
    data = request.get_json()
    vendor_email = get_jwt_identity()
    vendor_id = Vendor().fetch_specific_vendor(
        'id', f"email = '{vendor_email}'", 'vendors')

    if not vendor_id:
        return jsonify({
            "error": "Forbidden request!"
        }), 403

    if len(data['product_name']) < 2:
        return jsonify({
            "error": "Product name should be more descriptive"
        }), 422
    elif len(data['description']) < 10:
        return jsonify({
            "error": "Product description too short"
        }), 422
    elif type(data['quantity']) != int:
        return jsonify({
            "error": "Invalid quantity"
        }), 422
    elif type(data['regular_price']) != int:
        return jsonify({
            "error": "Invalid regular_price"
        }), 422
    elif type(data['discounted_price']) != int:
        return jsonify({
            "error": "Invalid discounted_price"
        }), 422
    elif type(data['product_rating']) != int:
        return jsonify({
            "error": "Invalid product_rating"
        }), 422
    elif type(data['mass']) != str:
        return jsonify({
            "error": "Invalid mass"
        }), 422

    product_data = {
        "product_name": data['product_name'],
        "product_id": str(uuid.uuid4()),
        "description": data['description'],
        "quantity": data['quantity'],
        "regular_price": data['regular_price'],
        "discounted_price": data['discounted_price'],
        "product_rating": data['product_rating'],
        "mass": data['mass'],
        "vendor_id": vendor_id[0]
    }
    product = Product(product_data)
    product.save_product()

    return jsonify({
        "message": "Product posted successfully"
    }), 201


# endpoint to update product
@v1.route("/product/update/<string:productId>", methods=['PUT'])
@jwt_required
def update_product(productId):
    data = request.get_json()
    vendor_email = get_jwt_identity()
    vendor_id = Vendor().fetch_specific_vendor(
        'id', f"email = '{vendor_email}'", 'vendors')[0]
    product = Product().fetch_specific_product(
        'vendor_id',
        f"product_id = '{productId}' AND vendor_id = '{vendor_id}'",
        'products')

    if not product:
        return jsonify({
            "Error": "Forbidden request!"
        }), 403
    elif len(data['product_name']) < 2:
        return jsonify({
            "error": "Product name should be more descriptive"
        }), 422
    elif len(data['description']) < 10:
        return jsonify({
            "error": "Product description too short"
        }), 422
    elif type(data['quantity']) != int:
        return jsonify({
            "error": "Invalid quantity"
        }), 422
    elif type(data['regular_price']) != int:
        return jsonify({
            "error": "Invalid regular_price"
        }), 422
    elif type(data['discounted_price']) != int:
        return jsonify({
            "error": "Invalid discounted_price"
        }), 422
    elif type(data['product_rating']) != int:
        return jsonify({
            "error": "Invalid product_rating"
        }), 422
    elif type(data['mass']) != str:
        return jsonify({
            "error": "Invalid mass"
        }), 422

    product_data = {
        "product_name": data['product_name'],
        "description": data['description'],
        "quantity": data['quantity'],
        "regular_price": data['regular_price'],
        "discounted_price": data['discounted_price'],
        "product_rating": data['product_rating'],
        "mass": data['mass']
    }

    try:
        Product().update_product(productId, product_data)

        return jsonify({
            "msg": "Product updated successfully"
        }), 200
    except Exception as e:
        print('--> ', e)


# endpoint to delete product
@v1.route("/product/delete/<string:productId>", methods=['DELETE'])
@jwt_required
def delete_product(productId):
    vendor_email = get_jwt_identity()
    vendor_id = Vendor().fetch_specific_vendor(
        'id', f"email = '{vendor_email}'", 'vendors')[0]
    product = Product().fetch_specific_product(
        'vendor_id',
        f"product_id = '{productId}' AND vendor_id = '{vendor_id}'",
        'products')

    if not product:
        return jsonify({
            "Error": "Forbidden request!"
        }), 403

    try:
        Product().delete_product(productId)

        return jsonify({
            "msg": "Product deleted successfully"
        }), 200
    except Exception as e:
        print('--> ', e)


# rate a product
@v1.route("/product/rate/<string:productId>", methods=['PATCH'])
@jwt_required
def rate_product(productId):
    data = request.get_json()
    user_email = get_jwt_identity()
    product = Product().fetch_specific_product(
        'vendor_id',
        f"product_id = '{productId}'",
        'products')
    
    if not product:
        return jsonify({
            "error": "Product not found!"
        }), 404
    vendor = Vendor().fetch_specific_vendor(
        'email', f"id = '{product[0]}'", 'vendors')

    if data['rating'] > 5:
        return jsonify({
            "error": "Ratings range from 0-5"
        }), 422
    elif not isinstance(data['rating'], int) or data['rating'] < 0:
        return jsonify({
            "error": "Invalid rating"
        }), 422
    elif user_email == vendor[0]:
        return jsonify({
            "error": "Sorry! You cannot rate your own product"
        }), 403

    try:
        Product().rate_product(productId, data['rating'])
    except Exception as e:
        print('--> ',e)

    return jsonify({
        "msg": "Product was rated successfully"
    }), 200