"""
This module defines all the reviews endpoints
"""
import json
from flask import request, jsonify, make_response, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.api.v1.models.product_model import Product
from app.api.v1.models.review_model import Review
from app.api.v1.models.user_model import User

v1 = Blueprint('reviewv1', __name__, url_prefix='/api/v1')

# endpoint to get all reviews
@v1.route("/reviews/<int:productId>", methods=['GET'])
def get_reviews(productId):
    reviews_list = []
    reviews = Review().fetch(
        '(product_id, user_id, review, product_rating, created_on)', f"product_id = '{productId}'", 'reviews')

    for review in reviews:
        parsed_review = eval(review[0])
        
        review_item = {
            "product_id": parsed_review[0],
            "user_id": parsed_review[1],
            "review": parsed_review[2],
            "rating": parsed_review[3],
            "created_on": parsed_review[4]
        }
        
        reviews_list.append(review_item)

    return jsonify({
        "status": 200,
        "review": reviews_list
    }), 200


# endpoint to post a review
@v1.route("/reviews/post/<int:productId>", methods=['POST'])
@jwt_required
def post_review(productId):
    data = request.get_json()
    user_email = get_jwt_identity()

    if (data['product_rating'] > 5) or (data['product_rating'] < 0):
        return jsonify({
            "error": "Ratings only range from 1-5"
        }), 422
    elif (len(data['review']) < 3) and (not isinstance(data['review'], str)):
        return jsonify({
            "error": "Please write a more descriptive review"
        }), 422
    
    try:
        user_id = User().fetch_specific_user(
            'id',
            f"email = '{user_email}'",
            'users'
        )
        review = {
            "review": data['review'],
            "product_rating": data['product_rating'],
            "product_id": productId,
            "user_id": user_id[0]
        }

        post_review = Review(review)
        post_review.save()

        return jsonify({
            "msg": "Review posted successfully!"
        }), 201
    except:
        return jsonify({
            "error": "User not found!"
        }), 404


# endpoint update a review
@v1.route("/reviews/update/<int:reviewId>", methods=['PUT'])
@jwt_required
def update_review(reviewId):
    data = request.get_json()
    user_email = get_jwt_identity()

    if (data['product_rating'] > 5) or (data['product_rating'] < 0):
        return jsonify({
            "error": "Ratings only range from 1-5"
        }), 422
    elif (len(data['review']) < 3) and (not isinstance(data['review'], str)):
        return jsonify({
            "error": "Please write a more descriptive review"
        }), 422

    updates = {
        "review": data['review'],
        "product_rating": data['product_rating']
    }
    
    try:
        user_id = User().fetch_specific_user('id', f"email = '{user_email}'" ,'users')
        review = Review().update(reviewId, updates, user_id[0])
    except:
        return jsonify({
            "error": "User not found!"
        }), 404

    if isinstance(review, dict):
        return jsonify(review), review['status']
    return jsonify({
        "msg": "Review updated successfully!"
    }), 201


# endpoint delete a review
@v1.route("/reviews/delete/<int:reviewId>", methods=['DELETE'])
@jwt_required
def delete_review(reviewId):
    email = get_jwt_identity()
    
    try:
        user_id = User().fetch_specific_user('id', f"email = '{email}'" ,'users')
        review = Review().delete(reviewId, user_id[0])
    except:
        return jsonify({
            "error": "User not found!"
        }), 404

    if isinstance(review, dict):
        return jsonify(review), review['status']
    return jsonify({
        "msg": "Review deleted successfully!"
    }), 201

