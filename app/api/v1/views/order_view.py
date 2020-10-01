from flask_jwt_extended import jwt_required
from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import hashlib, time, json

from app.api.v1.utils.transact_mpesa import lipa_na_mpesa
from app.api.v1.models.user_model import User
from app.api.v1.models.vendor_model import Vendor
from app.api.v1.models.order_model import Order


v1 = Blueprint('paymentv1', __name__, url_prefix='/api/v1')
valid_order_status = ['pending', 'confirmed', 'shipping', 'cancelled', 'delivered']

# Lipa na mpesa route
@v1.route("/lipa_mpesa")
@jwt_required
def lipa():
    return jsonify({
        "paid": lipa_na_mpesa()
    }), 200


# Get customer orders
@v1.route("/my-orders")
@jwt_required
def my_orders():
    user_email = get_jwt_identity()
    user_id = User().fetch_specific_user('id', f"email = '{user_email}'", 'users')
    
    if not user_id:
        return jsonify({
            "error": "Forbidden request!"
        }), 403

    try:
        orders = Order().fetch(
            '(customer_id, tracking_id, items, status, total)', f"customer_id = '{user_id[0]}'")
        orders_list = []

        for item in orders:

            order_item = {
                "customer_id": eval(item[0])[0],
                "tracking_id": eval(item[0])[1].strip(),
                "items": eval(item[0])[2].strip().split(', '),
                "status": eval(item[0])[3].strip(),
                "total": eval(item[0])[4]
            }
            
            orders_list.append(order_item)
    except Exception as e:
        print('--> ', e)

    return jsonify({
        "orders": orders_list
    }), 200


# Place an order
@v1.route("/place-order", methods=['POST'])
@jwt_required
def place_order():
    data = request.get_json()
    user_email = get_jwt_identity()
    hash_combo = current_app.config['SECURITY_PASSWORD_SALT'] + user_email + str(time.time())
    encode_hash_combo = hash_combo.encode('utf-8')
    hashed_value = hashlib.sha256(encode_hash_combo).hexdigest()[:5]
    
    customer_id = User().fetch_specific_user('id', f"email = '{user_email}'", 'users')
    
    # Grab vendors from data['items'] here:

    order_items = ', '.join(data['items'])

    # Fetch respective product vendors and verify them here
    
    if not customer_id:
        return jsonify({
            "msg": "Forbidden request!"
        }), 403
    
    order_dict = {
        "tracking_id": hashed_value,
        "customer_id": customer_id[0],
        "items": order_items, # list of product IDs
        # Add vendor field here
        "total": data['total']
    }

    order = Order(order_dict)

    try:
        order.save()
        # Send notification to vendor
    except Exception as e:
        print('--> ',e)

    return jsonify({
        "msg": "Order placed successfully"
    }), 201

    
# Update an order
@v1.route("/update-order/<string:tracking_id>", methods=['PATCH'])
@jwt_required
def update_order(tracking_id):
    data = request.get_json()
    user_email = get_jwt_identity()
    vendor = Vendor().fetch_specific_vendor('id', f"email = '{user_email}'", 'vendors')

    # Fetch respective product vendors and verify them here

    if not vendor:
        return jsonify({
            "error": "Forbidden request!"
        }), 403
    elif not (data['status'] in valid_order_status):
        return jsonify({
            "error": "Invalid status"
        }), 422
    
    updates = {
        "status": data['status']
    }

    update_order = Order().update(tracking_id, updates)

    # Send notification to user

    if isinstance(update_order, dict):
        return jsonify(update_order), update_order['status']
        
    return jsonify({
        "msg": "Order updated successfully"
    }), 200