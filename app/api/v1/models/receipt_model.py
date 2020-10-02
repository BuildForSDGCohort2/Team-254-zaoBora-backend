from app.api.v1.models.base_model import BaseModel


class Receipt(BaseModel):
    # model class for receipt

    def __init__(self, receipt={}):
        
        self.base_model = BaseModel()
        self.base_model.table_name = 'receipts'
        
        if receipt:
            self.discount = receipt['discount']
            self.delivery_fee = receipt['delivery_fee']
            self.subtotal = receipt['subtotal']
            self.total = receipt['total']
            self.customer_id = receipt['customer_id']
            self.tracking_id = receipt['tracking_id']

    def save(self):
        """ This method saves a receipt """

        receipt_item = dict(
            discount = self.discount,
            delivery_fee = self.delivery_fee,
            subtotal = self.subtotal,
            total = self.total,
            customer_id = self.customer_id,
            tracking_id = self.tracking_id
        )

        keys = ", ".join(receipt_item.keys())
        values = tuple(receipt_item.values())

        try:
            return self.base_model.add_item(keys, values)
        except Exception as e:
            print('----> ',e)

    def fetch(self, fields, condition):
        """ This method fetches order's receipt """

        try:
            return self.base_model.grab_all_items(fields, condition)
        except Exception as e:
            print('----> ',e)