from flask import jsonify
from app.api.v1.models.base_model import BaseModel


class Product(BaseModel):
    # model class for products
    
    def __init__(self, product={}):
        
        self.base_model = BaseModel()
        self.base_model.table_name = 'products'
        
        if product:
            self.pname = product['product_name']
            self.description = product['description']
            self.quantity = product['quantity']
            self.rprice = product['regular_price']
            self.dprice = product['discounted_price']
            self.prating = product['product_rating']
            self.preview = product['mass']
            self.vendor_id = product['vendor_id']
    
    def save_product(self):
        # func to save a non-existing product / new product
        
        product = dict(
            product_name=self.pname,
            description=self.description,
            quantity=self.quantity,
            regular_price=self.rprice,
            discounted_price=self.dprice,
            product_rating=self.prating,
            product_review=self.preview,
            vendor_id=self.vendor_id
        ) 
        
        keys = ", ".join(product.keys())
        values = tuple(product.values())
        
        return self.base_model.add_item(keys, values)
            
    def  fetch_product_id(self, product_name):
         # fetches a product id 
          
         try:
             return self.fetch_specific_product('id', f"product_name = '{product_name}'", 'products')
         except:
             return False
    
    def fetch_all_products(self, fields, condition, name):
        # fetches all products
        
        return self.base_model.grab_all_items(fields, condition, name)
    
    def fetch_specific_product(self, cols, condition, name):
        #  fetches a single product
        
        return self.base_model.grab_items_by_name(cols, condition, name)
    
    def update_product(self, id, updates):
        # updates a product
        
        pairs_dict = {
            "product_name": f"product_name = '{updates['product_name']}'", 
            "description": f"description = '{updates['description']}'", 
            "quantity": f"quantity = '{updates['quantity']}'", 
            "regular_price": f"regular_price = '{updates['regular_price']}'", 
            "discounted_price": f"discounted_price = '{updates['discounted_price']}'"     
        }
        
        pairs = ", ".join(pairs_dict.values())
        
        if self.fetch_specific_product('id', f"id = {id}", 'products'):
            return self.base_model.update_item(pairs, f"id = {id}", 'products')
        else:
            return jsonify({
                "error": "Product not found or does not exist!",
                "status": 404
            }), 404
            
    def delete_product(self, id):
        # defines the delete query
        
        if self.fetch_specific_product('id', f"id = {id}", 'products'):
            return self.base_model.delete_item(f"id = {id}", 'products')
        else:
            return {
                "error": "Product not found or does not exist!"
            }