"""
This module sets up all the reviews endpoints
"""

from flask import Blueprint
from flask import request, jsonify, make_response, Blueprint, session

from ..models.product_model import Product
from ..utils.reviews_validator import ReviewsValidator
from ..models.review_model import Review
from ..models.user_model import User

v1 = Blueprint('reviewv1', __name__, url_prefix='/api/v1/')

# endpoint to get a review
@v1.route("/<int:productId>/reviews", methods=['GET'])
def get_reviews(productId):

    if Product().fetch_specific_product('vendor_id', f"id = {productId}", 'products'):
        reviews = Review().fetch_reviews('(review, prodcut_id, user_id, id)', f'product_id = {productId}', 'reviews')
        reviews_list = []

        for review in reviews:
            parsed_review = eval(review[0])
            username = User().fetch_specific_user('username', f"id = {parsed_review[2]}", 'users')[0]

            obj = {
                "review": parsed_review[0],
                "product_id": parsed_review[1],
                "user_id": parsed_review[2],
                "username": username,
                "id": parsed_review[3]
            }
            reviews_list.append(obj)

        return make_response(jsonify({
            "status": 200,
            "reviews": reviews_list
        }), 200)
    else:
        return make_response(jsonify({
            "error": "product not found or does not exist",
            "status": 404
        }), 404)

# endpoint to post a review on a product
@v1.route("/<int:userId>/<int:productId>/reviews", methods=['POST'])
def review_on_product(productId, userId):
    data = request.get_json()
    auth_token = request.headers.get('Authorization')
    token = auth_token.split(" ")[1]

    try:
        data['review']
        review = ReviewsValidator(data['review'])
        if review.valid_review():
            return make_response(jsonify({
                "error": review.valid_review(),
                "status": 422
            }), 422)
    except:
        return make_response(jsonify({
            "error": 'You missed the review key',
            "status": 400
        }), 400)

    if not Product().fetch_specific_product('id', f"id = {productId}", 'products'):
        return make_response(jsonify({
            "error": "product not found or does not exist",
            "status": 404
        }), 404)
    elif not User().fetch_specific_user('id', f"id = {userId}", 'users'):
        return make_response(jsonify({
            "error": "User not found or does not exist",
            "status": 404
        }), 404)
    else:
        review = {
            "userId": userId,
            "review": data['review'],
            "productId": productId,
        }

        review_model = review(review)

        review_model.save_review()

        if not User().blacklisted(token):
            return make_response(jsonify({
                "status": 201,
                "message": "You have successfully reviewed on this product",
                "data": [{
                    "product": productId,
                    "review": review['review']
                }]
            }), 201)
        else:
            return make_response(jsonify({
                "error": 'Please log in first',
                "status": 401
            }), 401)

# endpoint to update a review
@v1.route("/<int:userId>/<int:productId>/reviews/<int:reviewId>", methods=['PUT'])
def edit_review(userId, reviewId, productId):
    data = request.get_json()
    auth_token = request.headers.get('Authorization')
    token = auth_token.split(" ")[1]

    try:
        data['review']
        review = ReviewsValidator(data['review'])
        if review.valid_review():
            return make_response(jsonify({
                "error": review.valid_review(),
                "status": 422
            }), 422)
    except:
        return make_response(jsonify({
            "error": 'You missed the review key, value pair'
        }), 400)

    if not Product().fetch_specific_product('id', f"id = {productId}", 'products'):
        return make_response(jsonify({
            "error": "product not found or does not exist",
            "status": 404
        }), 404)
    elif not User().fetch_specific_user('id', f"id = {userId}", 'users'):
        return make_response(jsonify({
            "error": "User not found or does not exist",
            "status": 404
        }), 404)

    try:
        review().fetch_specific_review('user_id', f"id = {reviewId}", 'reviews')[0]
        if review().fetch_specific_review('user_id', f"id = {reviewId}", 'reviews')[0] == userId:

            review = review().update_review(reviewId, data)

            if isinstance(review, dict):
                return make_response(review, 404)
            else:

                if not User().blacklisted(token):
                    return make_response(jsonify({
                        "message": "You have successfully updated this review",
                        "review": data['review'],
                        "status": 200
                    }), 200)
                else:
                    return make_response(jsonify({
                        "error": 'Please log in first',
                        "status": 403
                    }), 403)
        else:
            return make_response(jsonify({
                "error": "You are not authorized to perform this action!",
                "status": 401
            }), 401)
    except:
        return make_response(jsonify({
            "error": "review not found or does not exist!",
            "status": 404
        }), 404)

# endpoint to delete a review
@v1.route("/<int:userId>/<int:productId>/reviews/<int:reviewId>", methods=['DELETE'])
def delete_review(userId, productId, reviewId):
    auth_token = request.headers.get('Authorization')
    token = auth_token.split(" ")[1]

    if not Product().fetch_specific_product('id', f"id = {productId}", 'products'):
        return make_response(jsonify({
            "error": "product not found or does not exist",
            "status": 404
        }), 404)
    elif not User().fetch_specific_user('id', f"id = {userId}", 'users'):
        return make_response(jsonify({
            "error": "User not found or does not exist",
            "status": 404
        }), 404)

    try:
        Review().fetch_specific_review('user_id', f"id = {reviewId}", 'reviews')[0]
        if Review().fetch_specific_review('user_id', f"id = {reviewId}", 'reviews') == (userId,):

            print('--->', Review().fetch_specific_review('user_id', f"id = {reviewId}", 'reviews'))
            print('--->', (userId,))

            if not User().blacklisted(token):
                Review().delete_review(reviewId)
                return make_response(jsonify({
                    "message": 'review was deleted successfully',
                    "status": 200
                }), 200)
            else:
                return make_response(jsonify({
                    "error": 'Please log in first',
                    "status": 401
                }), 401)
        else:
            return make_response(jsonify({
                "error": "You are not authorized to perform this action!",
                "status": 401
            }), 401)
    except:
        return make_response(jsonify({
            "error": "review not found or does not exist",
            "status": 404
        }), 404)
