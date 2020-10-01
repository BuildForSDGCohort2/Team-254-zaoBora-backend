from app.api.v1.models.base_model import BaseModel
from app.api.v1.models.vendor_model import Vendor


class Order(BaseModel):
    # model class for order

    def __init__(self, order={}):
        
        self.base_model = BaseModel()
        self.base_model.table_name = 'orders'
        
        if order:
            self.customer_id = order['customer_id']
            self.tracking_id = order['tracking_id']
            self.items = order['items']
            self.total = order['total']

    def save(self):
        """ This method saves a order """

        order_item = dict(
            customer_id = self.customer_id,
            tracking_id = self.tracking_id,
            items = self.items,
            total = self.total
        )

        keys = ", ".join(order_item.keys())
        values = tuple(order_item.values())

        try:
            return self.base_model.add_item(keys, values)
        except Exception as e:
            print('----> ',e)

    def fetch(self, fields, condition):
        """ This method fetches product's order """

        try:
            return self.base_model.grab_all_items(fields, condition)
        except Exception as e:
            print('----> ',e)


    def update(self, tracking_id, updates):
        """ This method updates a order """

        pairs_dict = {
            "status": f"status = '{updates['status']}'",
        }
        
        pairs = ", ".join(pairs_dict.values())
        order = self.fetch('id', f"tracking_id = '{tracking_id}'")

        if not order:
            return {
                "error": "order not found or does not exist!",
                "status": 404
            }
        else:
            return self.base_model.update_item(pairs, f"tracking_id = '{tracking_id}'", 'orders')