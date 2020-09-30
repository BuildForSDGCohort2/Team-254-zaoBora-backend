from app.api.v1.models.base_model import BaseModel


class Review(BaseModel):
    # model class for reviews

    def __init__(self, review={}):
        
        self.base_model = BaseModel()
        self.base_model.table_name = 'reviews'
        
        if review:
            self.product_rating = review['product_rating']
            self.review = review['review']
            self.product_id = review['product_id']
            self.user_id = review['user_id']

    def save(self):
        """ This method saves a review """

        review_item = dict(
            user_id=self.user_id,
            product_id=self.product_id,
            review=self.review,
            product_rating=self.product_rating
        )

        keys = ", ".join(review_item.keys())
        values = tuple(review_item.values())
        return self.base_model.add_item(keys, values)

    def fetch(self, fields, condition, name):
        """ This method fetches product's reviews """

        return self.base_model.grab_all_items(fields, condition, name)

    def update(self, id, updates, user_id):
        """ This method updates a review """

        pairs_dict = {
            "review": f"review = '{updates['review']}'",
            "product_rating": f"product_rating = '{updates['product_rating']}'",
        }
        
        pairs = ", ".join(pairs_dict.values())
        review = self.fetch('id, user_id', f"id = {id}", 'reviews')

        if not review:
            return {
                "error": "review not found or does not exist!",
                "status": 404
            }
        elif review[0][1] != user_id:
            return {
                "error": "Forbiden request!",
                "status": 403
            }
        else:
            return self.base_model.update_item(pairs, f"id = '{id}'", 'reviews')


    def delete(self, id, user_id):
        """ This method deletes a review """
        review = self.fetch('id, user_id', f"id = {id}", 'reviews')
        
        if review[0][1] != user_id:
            return {
                "error": "Forbiden request!",
                "status": 403
            }

        return self.base_model.delete_item(f"id = '{id}'")