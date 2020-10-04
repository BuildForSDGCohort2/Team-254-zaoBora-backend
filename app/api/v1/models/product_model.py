from app.api.v1.models.base_model import BaseModel


class Product(BaseModel):
    # model class for products
    
    def __init__(self, product={}):
        
        self.base_model = BaseModel()
        self.base_model.table_name = 'products'
        
        if product:
            self.product_name = product['product_name']
            self.product_id = product['product_id']
            self.description = product['description']
            self.quantity = product['quantity']
            self.regular_price = product['regular_price']
            self.discounted_price = product['discounted_price']
            self.product_rating = product['product_rating']
            self.mass = product['mass']
            self.vendor_id = product['vendor_id']
    
    def save_product(self):
        # func to save a non-existing product / new product
        
        product = dict(
            product_name=self.product_name,
            product_id=self.product_id,
            description=self.description,
            quantity=self.quantity,
            regular_price=self.regular_price,
            discounted_price=self.discounted_price,
            product_rating=self.product_rating,
            mass=self.mass,
            vendor_id=self.vendor_id
        ) 
        
        keys = ", ".join(product.keys())
        values = tuple(product.values())
        
        return self.base_model.add_item(keys, values)
    
    def fetch_all_products(self, fields, condition, name):
        # fetches all products
        
        return self.base_model.grab_all_items(fields, condition, name)
    
    def fetch_specific_product(self, cols, condition, name):
        #  fetches a single product
        
        return self.base_model.grab_items_by_name(cols, condition, name)
    
    def update_product(self, product_id, updates):
        # updates a product
        
        pairs_dict = {
            "product_name": f"product_name = '{updates['product_name']}'", 
            "description": f"description = '{updates['description']}'", 
            "quantity": f"quantity = '{updates['quantity']}'", 
            "regular_price": f"regular_price = '{updates['regular_price']}'",
            "discounted_price": f"discounted_price = '{updates['discounted_price']}'",
            "product_rating": f"product_rating = '{updates['product_rating']}'",
            "mass": f"mass = '{updates['mass']}'"
        }
        
        pairs = ", ".join(pairs_dict.values())
        
        return self.base_model.update_item(pairs, f"product_id = '{product_id}'", 'products')
            
    def delete_product(self, product_id):
        # defines the delete product query
        
        return self.base_model.delete_item(f"product_id = '{product_id}'", 'products')

    def rate_product(self, product_id, rating):
        
        pairs_dict = {
            "product_rating": f"product_rating = '{rating}'"
        }
        
        updates = ", ".join(pairs_dict.values())
        
        return self.base_model.update_item(updates, f"product_id = '{product_id}'", 'products')