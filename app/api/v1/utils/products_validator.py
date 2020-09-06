import re
import string
from datetime import datetime

class ProductValidator:

    def __init__(self, data={}):
        self.data = data
        
    # helper methods
    
    def errorHandler(self, error_name):
        errors = {
            "product_name": "Your ",
            "description": "Enter a valid description",
            "quantity":"Enter quantity",
            "regular_price":"Enter price",
            "discounted_price": "Enter discounted"   
        }
        return errors[error_name]
    
    def check_fields(self, data, fields):
        for key in fields:
            try:
                data[key]
            except:
                return {
                    "error": 'You missed the {} key, value pair'.format(key),
                    "status": 400
                }
                
    # validator methods
    def product_fields(self, data):
        
        fields = ['product_name', 'description', 'quantity', 'regular_price', 'discounted_price']
        
        return self.check_fields(data, fields) 
