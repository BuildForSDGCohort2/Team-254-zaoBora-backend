from app.api.v1.models.base_model import BaseModel


class Cart(BaseModel):
    # model class for cart

    def __init__(self, cart={}):
        
        self.base_model = BaseModel()
        self.base_model.table_name = 'cart'
        
        if cart:
            self.customer_id = cart['customer_id']
            self.product_id = cart['product_id']
            self.quantity = cart['quantity']
            self.unit_price = cart['unit_price']
            self.total = cart['total']

    def save(self):
        """ This method saves a cart """

        cart_item = dict(
            customer_id = self.customer_id,
            product_id = self.product_id,
            quantity = self.quantity,
            unit_price = self.unit_price,
            total = self.total
        )

        keys = ", ".join(cart_item.keys())
        values = tuple(cart_item.values())
        return self.base_model.add_item(keys, values)

    def fetch(self, fields, condition, name):
        """ This method fetches product's cart """

        return self.base_model.grab_all_items(fields, condition, name)

    def update(self, id, updates, user_id):
        """ This method updates a cart """

        pairs_dict = {
            "quantity": f"quantity = '{updates['quantity']}'",
            "total": f"total = '{updates['total']}'",
        }
        
        pairs = ", ".join(pairs_dict.values())
        cart = self.fetch('id, customer_id', f"id = {id}", 'cart')

        if not cart:
            return {
                "error": "cart not found or does not exist!",
                "status": 404
            }
        elif cart[0][1] != user_id:
            return {
                "error": "Forbiden request!",
                "status": 403
            }
        else:
            return self.base_model.update_item(pairs, f"id = '{id}'", 'cart')


    def delete(self, id, user_id):
        """ This method deletes a cart """
        cart = self.fetch('id, customer_id', f"id = {id}", 'cart')
        
        if cart[0][1] != user_id:
            return {
                "error": "Forbiden request!",
                "status": 403
            }

        return self.base_model.delete_item(f"id = '{id}'")