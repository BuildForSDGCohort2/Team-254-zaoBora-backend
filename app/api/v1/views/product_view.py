"""
This module defines all the user endpoints
"""
import json
from flask import request, jsonify, make_response, Blueprint

from ..models.product_model import Product, AuthenticationRequired
from ..models.user_model import User

v1 = Blueprint('productv1', __name__, url_prefix='/api/v1')

# endpoint to get all products
@v1.route("/products", methods=['GET'])
def get():
    products = Product().fetch_all_products('(product_name, description, quantity, regular_price, id, discounted_price, product_rating, created_on, farmer_id)', 'True = True', 'products')
    products_list = []
        
    for product in products:
        username = User().fetch_specific_user('username', f"id = {product[0]}", 'users')[0]
        print('output:', username)
        product_item = dict({
            "product_name": product[0],
            "description": product[0][2],
            "quantity": product[0][3],
            "regular_price": product[0][4],
            "id": product[0][5],
            "discounted_price": product[0][6],
            "product_rating": product[0][7],
            "product_review": product[0][8],
            "created_on": product[0][9],
            "farmer_id": product[0][10],
            # "farmer": username
        })
        res = eval(product[0])
        print('Output Two:', product_item) 
        print ('Output==>', type(product[0]))
        print ('Output====>', tuple(product[0]))
        print ('Output<==>', res)
        
        
        products_list.append(product_item)

    return jsonify({
        "status": 200,
        "products": products_list
    }), 200

    
# endpoint to fetch a single product
@v1.route("products/<int:productId>", methods=['GET'])
def get_product(productId):
    try:
        product = Product().grab_items('(product_name, description, quantity, regular_price, id, discounted_price, product_rating, product_review, created_on, farmer_id)', f'id ={productId}', 'products')
        username = User().fetch_specific_user('username', f'id = {product[0][10]}')[0]
        
        product_item = {
            "product_name": product[0][1],
            "description": product[0][2],
            "quantity": product[0][3],
            "regular_price": product[0][4],
            "id": product[0][5],
            "discounted_price": product[0][6],
            "product_rating": product[0][7],
            "product_review": product[0][8],
            "created_on": product[0][9],
            "farmer_id": product[0][10],
            "farmer": username
        }
        return jsonify({
            "product": product_item,
            "status": 200
        })
    except:
        return jsonify({
            "error": "product not found",
            "status": 404
        }), 404    

# endpoint to register up new products
@v1.route("/create/product", methods=['POST'])
def registration():
    data = request.get_json()
    
    # Register product
    product_data = {
        "product_name": data['product_name'],
        "description": data['description'],
        "quantity": data['quantity'],
        "regular_price": data['regular_price'],
        "discounted_price": data['discounted_price']
    }
    
    reg_product = Product(product_data) 
    
    if reg_product.save_product():
        return make_response(jsonify(reg_product.save_product()), 409)
    else:
        id = reg_product.fetch_product_id(product_data['product_name'])
        
        return make_response(jsonify({
            "status": 201,
            "message": "{} registered successfully".format(data['product_name']),
            "product's details": data
        }), 201)
        
# endpoint to delete product
@v1.route("/product/<int:productId>", methods=['DELETE'])
def del_product(productId):
    
    remove_product = Product().delete_product(productId)
    
    if isinstance(remove_product, dict):
        return make_response(jsonify(remove_product), 404)
    else:
        return make_response(jsonify({
            "message": f"product with id '{productId}' deleted successfully",
            "status": 200
        }), 200)