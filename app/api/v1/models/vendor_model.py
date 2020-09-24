from flask import jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.api.v1.models.base_model import BaseModel

class Vendor(BaseModel):
    #  model class for vendor object

    def __init__(self, vendor={}):

        self.base_model = BaseModel()
        self.base_model.tablename = 'vendors'

        if vendor:
              self.fname = vendor['first_name']
              self.lname = vendor['last_name']
              self.email = vendor['email']
              self.username = vendor['username']
              self.phone_number = vendor['phone_number']
              self.address = vendor['address']
              self.region = vendor['region']
              self.city = vendor['city']
              self.street_address = vendor['street_address']
              self.password = generate_password_hash(vendor['password'])

    def save_vendor(self):
    # func to save new vendor
        vendor = dict(
            first_name=self.fname,
            last_name=self.lname,
            email=self.email,
            phone_number=self.phone_number,
            username=self.username,
            address=self.address,
            region=self.region,
            city=self.city,
            street_address=self.street_address,
            password=self.password
        )

        keys = ", ".join(vendor.keys())
        values = tuple(vendor.values())

        if self.fetch_specific_vendor('email', f"email = '{self.email}'", 'vendors'):
            return {
                "error": "This email already exists try logging In!",
                "status": 409
            }
        elif self.fetch_specific_vendor('username', f"username = '{self.username}'", 'vendors'):
            return {
                "error": "This Username is already Taken!",
                "status": 409
            }
        else:
            return self.base_model.add_item(keys, values, 'vendors')

    def fetch_vendor_id(self, username):
        # fetches a vendor by id
        try:
            return self.fetch_specific_vendor('id', f"username = '{username}'", 'vendors')
        except:
            return False

    def fetch_all_vendors(self):
        # fetches all vendors

        return self.base_model.grab_all_items('(username, email, first_name, last_name)', f"True = True", 'vendors')

    def fetch_specific_vendor(self, cols, condition, name):
        # fetches a single vendor

        return self.base_model.grab_items_by_name(cols, condition, name)

    def log_in_vendor(self, details):
         # logs in a vendor

        vendor = self.fetch_specific_vendor('email', f"email = '{details['email']}'", 'vendors')
        password = self.fetch_specific_vendor('password', f"email = '{details['email']}'", 'vendors')
        
        if not vendor:
            return {
                "error": "Details not found. Try signing up!",
                "status": 401
            }
        elif not check_password_hash(password[0].strip(), details['password']):
            return {
                "error": "Your email or password is incorrect!",
                "status": 403
            }
        else:
            return self.base_model.grab_items('(id, username)', f"email = '{details['email']}'", 'vendors')[0]

    def log_out_vendor(self, vendor_email, id):
         # logs out a vendor

        vendor = self.fetch_specific_vendor('email', f"id = '{id}'", 'vendors')
        valid_vendor = vendor and vendor[0].strip()
        
        if valid_vendor and (valid_vendor == vendor_email):
            return valid_vendor
        else:
            return False

    def delete_vendor(self, email):
         # defines the delete query

        if self.fetch_specific_vendor('email', f"email = '{email}'", 'vendors'):
               return self.base_model.delete_item(f"email = '{email}'", 'vendors')
        else:
            return {
                "error": "Vendor not found or does not exist!"
            }

    def update_vendor(self, email, updates):
        # This method defines the update query
        
        pairs_dict = {
            "first_name": f"first_name = '{updates['first_name']}'",
            "last_name": f"last_name = '{updates['last_name']}'",
            "phone_number": f"phone_number = '{updates['phone_number']}'",
            "address": f"address = '{updates['address']}'",
            "region": f"region = '{updates['region']}'",
            "city": f"city = '{updates['city']}'",
            "street_address": f"street_address = '{updates['street_address']}'"
        }
        
        pairs = ", ".join(pairs_dict.values())

        if self.fetch_specific_vendor('email', f"email = '{email}'", 'vendors'):
            return self.base_model.update_item(pairs, f"email = '{email}'", 'vendors')
        else:
            return {
                "error": "Vendor not found or does not exist!",
                "status": 404
            }    
        