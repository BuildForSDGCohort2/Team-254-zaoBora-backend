from flask import jsonify
from .base_model import BaseModel, AuthenticationRequired


class Product(BaseModel):
    # model class for products object
    
    def __init__(self, product={}):
        
        self.base_model = BaseModel()
        self.base_model.table_name = 'products'
        
        if product:
            self.pname = product['product_name']
            self.description = product['description']
            self.quantity = product['quantity']
            self.rprice = product['regular_price']
            self.dprice = product['discounted_price']
    
    def save_product(self):
        # func to save a non-existing product / new product
        
        product = dict(
            product_name=self.pname,
            description=self.description,
            quantity=self.quantity,
            regular_price=self.rprice,
            discounted_price=self.dprice
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
        
        return self.base_model.grab_all_items('(product_name, description, quantity, regular_price, id, discounted_price, created_on, farmer_id)', condition, name) 
    
    def fetch_specific_product(self, cols, condition, name):
        #  fetches a single product
        
        return self.base_model.grab_items_by_name(cols, condition, name)
    
    def delete_product(self, id):
        #  # defines the delete query
        
        if self.fetch_specific_product('id', f"id = {id}", 'products'):
            return self.base_model.delete_item(f"id = {id}", 'products')
        else:
            return {
                "error": "Product not found or does not exist!"
            }