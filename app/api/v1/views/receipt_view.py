from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, Blueprint, request

from app.api.v1.models.receipt_model import Receipt
from app.api.v1.models.user_model import User
from app.api.v1.models.order_model import Order


v1 = Blueprint('receiptv1', __name__, url_prefix='/api/v1')

# Get customer receipts
@v1.route("/<string:trackingId>/receipt")
@jwt_required
def fetch_receipt(trackingId):
    user_email = get_jwt_identity()
    user_id = User().fetch_specific_user('id', f"email = '{user_email}'", 'users')
    receipt = Receipt().fetch(
        '(discount, delivery_fee, subtotal, total, customer_id, tracking_id, created_on)',
        f"tracking_id = '{trackingId}' AND customer_id = '{user_id[0]}'")

    if not receipt:
        return jsonify({
            "error": "Receipt does not exist!"
        }), 404

    receipt_tuple = eval(receipt[0][0])

    receipt_item = {
        "discount": receipt_tuple[0],
        "delivery_fee": receipt_tuple[1],
        "subtotal": receipt_tuple[2],
        "total": receipt_tuple[3],
        "customer_id": receipt_tuple[4],
        "tracking_id": receipt_tuple[5].strip(),
        "created_on": receipt_tuple[6]
    }

    return jsonify({
        "receipt": receipt_item
    }), 200


# Generate a receipt
@v1.route("/<int:order_id>/generate-receipt", methods=['POST'])
@jwt_required
def generate_receipt(order_id):
    data = request.get_json()
    user_email = get_jwt_identity()
    user_id = User().fetch_specific_user('id', f"email = '{user_email}'", 'users')[0]
    order = Order().fetch("tracking_id", f"customer_id = {user_id} AND id = {order_id}")

    if not order:
        return jsonify({
            "error": "Order does not exist!"
        }), 404
    tracking_id = order[0][0].strip()
    receipt = Receipt().fetch(
        '(discount, delivery_fee, subtotal, total, customer_id, tracking_id, created_on)',
        f"tracking_id = '{tracking_id}'")

    if not receipt:
        def error(field):
            return { "error": f"Invalid {field}" }

        if not isinstance(data['discount'], int):
            return jsonify(error('discount')), 422
        elif not isinstance(data['delivery_fee'], int):
            return jsonify(error('delivery_fee')), 422
        elif not isinstance(data['subtotal'], int):
            return jsonify(error('subtotal')), 422
        elif not isinstance(data['total'], int):
            return jsonify(error('total')), 422

        receipt = {
            "discount": data['discount'],
            "delivery_fee": data['delivery_fee'],
            "subtotal": data['subtotal'],
            "total": data['total'],
            "customer_id": user_id,
            "tracking_id": tracking_id
        }
        Receipt(receipt).save()

        return jsonify({
            "msg": "Receipt generated successfully!",
            "receipt": receipt
        }), 201

    receipt_tuple = eval(receipt[0][0])

    receipt_item = {
        "discount": receipt_tuple[0],
        "delivery_fee": receipt_tuple[1],
        "subtotal": receipt_tuple[2],
        "total": receipt_tuple[3],
        "customer_id": receipt_tuple[4],
        "tracking_id": receipt_tuple[5].strip(),
        "created_on": receipt_tuple[6]
    }

    return jsonify({
        "error": "Receipt already exists!",
        "receipt": receipt_item
    }), 409