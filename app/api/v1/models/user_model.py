from flask import jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.api.v1.models.base_model import BaseModel

class User(BaseModel):
    #  model class for user object

    def __init__(self, user={}):

        self.base_model = BaseModel()
        self.base_model.tablename = 'users'

        if user:
              self.fname = user['first_name']
              self.lname = user['last_name']
              self.email = user['email']
              self.username = user['username']
              self.is_farmer = user['is_farmer']
              self.phone_number = user['phone_number']
              self.address = user['address']
              self.region = user['region']
              self.city = user['city']
              self.street_address = user['street_address']
              self.password = generate_password_hash(user['password'])

    def save_user(self):
    # func to save new user
        user = dict(
            first_name=self.fname,
            last_name=self.lname,
            email=self.email,
            is_farmer=self.is_farmer,
            phone_number=self.phone_number,
            username=self.username,
            address=self.address,
            region=self.region,
            city=self.city,
            street_address=self.street_address,
            password=self.password
        )

        keys = ", ".join(user.keys())
        values = tuple(user.values())

        if self.fetch_specific_user('email', f"email = '{self.email}'", 'users'):
            return {
                "error": "This email already exists try logging In!",
                "status": 409
            }
        elif self.fetch_specific_user('username', f"username = '{self.username}'", 'users'):
            return {
                "error": "This Username is already Taken!",
                "status": 409
            }
        else:
            return self.base_model.add_item(keys, values, 'users')

    def fetch_user_id(self, username):
        # fetches a user by id
        try:
            return self.fetch_specific_user('id', f"username = '{username}'", 'users')
        except:
            return False

    def fetch_all_users(self):
        # fetches all users

        return self.base_model.grab_all_items('(username, email, first_name, last_name)', f"True = True", 'users')

    def fetch_specific_user(self, cols, condition, name):
        # fetches a single user

        return self.base_model.grab_items_by_name(cols, condition, name)

    def log_in_user(self, details):
         # logs in a user

        user = self.fetch_specific_user('email', f"email = '{details['email']}'", 'users')
        password = self.fetch_specific_user('password', f"email = '{details['email']}'", 'users')

        if not user:
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
            userDetails = self.base_model.grab_items(
                '(first_name, last_name, username, phone_number, email, city, region, address, street_address, is_farmer, email_confirmed)',
                f"email = '{details['email']}'",
                'users'
            )[0]

            return {
                "first_name": userDetails['f1'].strip(),
                "last_name": userDetails['f2'].strip(),
                "username": userDetails['f3'].strip(),
                "phone_number": userDetails['f4'].strip(),
                "email": userDetails['f5'].strip(),
                "city": userDetails['f6'].strip(),
                "region": userDetails['f7'].strip(),
                "address": userDetails['f8'].strip(),
                "street_address": userDetails['f9'].strip(),
                "is_farmer": userDetails['f10'],
                "email_confirmed": userDetails['f11']
            }

    # def log_out_user(self, user_auth_email, email):
    #      # logs out a user
        
    #     if user_auth_email == email:
    #         return True
    #     else:
    #         return False

    def delete_user(self, email):
         # defines the delete query

        if self.fetch_specific_user('email', f"email = '{email}'", 'users'):
               return self.base_model.delete_item(f"email = '{email}'", 'users')
        else:
            return {
                "error": "User not found or does not exist!"
            }

    def update_user(self, email, updates):
        # This method defines the update query
        
        pairs_dict = {
            "first_name": f"first_name = '{updates['first_name']}'",
            "last_name": f"last_name = '{updates['last_name']}'",
            "phone_number": f"phone_number = '{updates['phone_number']}'",
            "address": f"address = 'updates['address']'",
            "region": f"region = 'updates['region']'",
            "city": f"city = 'updates['city']'",
            "street_address": f"street_address = 'updates['street_address']'"
        }
        
        pairs = ", ".join(pairs_dict.values())

        if self.fetch_specific_user('email', f"email = '{email}'", 'users'):
            return self.base_model.update_item(pairs, f"email = '{email}'", 'users')
        else:
            return {
                "error": "User not found or does not exist!",
                "status": 404
            }

    def verify_email(self, email, account):
        # This method defines the update query
        
        pairs = "email_confirmed = true"

        if self.fetch_specific_user('email', f"email = '{email}'", account):
            self.base_model.update_item(pairs, f"email = '{email}'", account)
            return 'verified'
        else:
            return {
                "error": "User not found or does not exist!",
                "status": 404
            }
        