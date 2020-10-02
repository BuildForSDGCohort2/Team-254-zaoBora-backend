from flask import jsonify
from .base_model import BaseModel

class Review(BaseModel):

    def __init__(self, review={}):

        self.base_model = BaseModel()
        self.base_model.table_name = 'reviews'

        if review:
            self.product_rating = review['product_rating']
            self.review = review['review']
            self.user_id = review['userId']
            self.product_id = review['productId']

    def save_review(self):
        # func saves a review

        review_item = dict(
            user_id=self.user_id,
            product_id=self.product_id,
            review=self.review
        )

        keys = ", ".join(review_item.keys())
        values = tuple(review_item.values())
        self.base_model.add_item(keys, values)


    def fetch_reviews(self, fields, condition, name):
        # fetches all reviews

        return self.base_model.grab_all_items('(review, product_id, user_id, id)', f"True = True", 'reviews')

    def fetch_specific_review(self, column, condition, name):
        #  fetches a single review

        return self.base_model.grab_items_by_name(column, condition, name)

    def update_review(self, id, updates):
        # func to update a review

        pairs_dict = {
            "review": f"review = '{updates['review']}'",
        }

        pairs = ", ".join(pairs_dict.values())

        if self.fetch_specific_review('id', f"id = {id}", 'reviews'):
            return self.base_model.update_item(pairs, f"id = {id}", 'reviews')
        else:
            return jsonify({
                "error": "review not found or does not exist!",
                "status": 404
            })

    def delete_review(self, id):
        # func to delete a review

        return self.base_model.delete_item(f"id = {id}")
