"""
This module defines all the cart endpoints
"""
import json
from flask import request, jsonify, make_response, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api.v1.models.product_model import Product
from app.api.v1.models.user_model import User
from app.api.v1.models.cart_model import Cart

v1 = Blueprint('cartv1', __name__, url_prefix='/api/v1')

# endpoint to get all cart
@v1.route("/cart/<int:productId>", methods=['GET'])
@jwt_required
def get_cart(productId):
    cart_list = []
    get_jwt_identity()
    cart = Cart().fetch(
        '(product_id, customer_id, quantity, unit_price, total, created_on)', f"product_id = '{productId}'", 'cart')

    for i in cart:
        parsed_cart = eval(i[0])
        
        cart_item = {
            "product_id": parsed_cart[0],
            "customer_id": parsed_cart[1],
            "quantity": parsed_cart[2],
            "unit_price": parsed_cart[3],
            "total": parsed_cart[4],
            "created_on": parsed_cart[5]
        }
        
        cart_list.append(cart_item)

    return jsonify({
        "status": 200,
        "cart": cart_list
    }), 200


# endpoint to post a cart
@v1.route("/cart/post/<int:productId>", methods=['POST'])
@jwt_required
def post_cart(productId):
    data = request.get_json()
    user_email = get_jwt_identity()
    product = Product().fetch_specific_product('mass, discounted_price, quantity', f"id = '{productId}'" ,'products')

    if not product:
        return jsonify({
            "error": "Product not found"
        }), 404
    elif not isinstance(data['quantity'], int):
        return jsonify({
            "error": "Invalid quantity"
        }), 422
    elif (data['quantity'] > product[2]) or (data['quantity'] < 0):
        return jsonify({
            "error": f"only {product[2]} {product[0].strip()} is available"
        }), 422
    
    try:
        user_id = User().fetch_specific_user(
            'id',
            f"email = '{user_email}'",
            'users'
        )
        cart = {
            "customer_id": user_id[0],
            "product_id": productId,
            "quantity": data['quantity'],
            "unit_price": product[1],
            "total": data['total']
        }
        print('==> ',cart)

        post_cart = Cart(cart)
        post_cart.save()

        return jsonify({
            "msg": "cart posted successfully!"
        }), 201
    except:
        return jsonify({
            "error": "User not found!"
        }), 404


# endpoint update a cart
@v1.route("/cart/update/<int:cartId>", methods=['PUT'])
@jwt_required
def update_cart(cartId):
    data = request.get_json()
    user_email = get_jwt_identity()
    cart = Cart().fetch('mass, discounted_price', f"id = '{cartId}'" ,'products')

    if not cart:
        return jsonify({
            "error": "Cart not found"
        }), 404
    elif (not isinstance(data['quantity'], int)) or (data['quantity'] < 0):
        return jsonify({
            "error": "Invalid quantity"
        }), 422

    updates = {
        "quantity": data['quantity'],
        "total": data['total']
    }
    
    try:
        user_id = User().fetch_specific_user('id', f"email = '{user_email}'" ,'users')
        print('==> ',user_id)
        cart = Cart().update(cartId, updates, user_id[0])
    except:
        return jsonify({
            "error": "User not found!"
        }), 404

    if isinstance(cart, dict):
        return jsonify(cart), cart['status']
    return jsonify({
        "msg": "cart updated successfully!"
    }), 201


# endpoint delete a cart
@v1.route("/cart/delete/<int:cartId>", methods=['DELETE'])
@jwt_required
def delete_cart(cartId):
    email = get_jwt_identity()
    
    try:
        user_id = User().fetch_specific_user('id', f"email = '{email}'" ,'users')
        cart = Cart().delete(cartId, user_id[0])
    except:
        return jsonify({
            "error": "User not found!"
        }), 404

    if isinstance(cart, dict):
        return jsonify(cart), cart['status']
    return jsonify({
        "msg": "cart deleted successfully!"
    }), 201

