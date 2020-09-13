from flask import jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .base_model import BaseModel, AuthenticationRequired

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
              self.password = generate_password_hash(user['password'])
              self.is_admin = False

    def save_user(self):
    # func to save new user
     user = dict(
       first_name=self.fname,
       last_name=self.lname,
       email=self.email,
       username=self.username,
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

        return self.base_model.grab_all_items('(username, email)', f"True = True", 'users')

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
        elif not check_password_hash(password[0], details['password']):
            return {
                "error": "Your email or password is incorrect!",
                "status": 403
            }
        else:
            return self.base_model.grab_items('(id, username)', f"email = '{details['email']}'", 'users')[0]

    def log_out_user(self, id):
         # logs out a user

        user = self.fetch_specific_user('username', f"id = '{id}'", 'users')

        if user:
            return user[0]
        else:
            return False

    def delete_user(self, id):
         # defines the delete query

        if self.fetch_specific_user('id', f"id = {id}", 'users'):
               return self.base_model.delete_item(f"id = {id}", 'users')
        else:
            return {
                "error": "User not found or does not exist!"
            }

    def update_user(self, id, updates):
        # This method defines the update query
        
        pairs_dict = {
            "first_name": f"first_name = '{updates['first_name']}'",
            "last_name": f"last_name = '{updates['last_name']}'",
            "email": f"email = '{updates['email']}'",
            "username": f"username = '{updates['username']}'",
            "password": f"password = '{generate_password_hash(updates['password'])}'"
        }
        
        pairs = ", ".join(pairs_dict.values())
        
        if self.fetch_specific_user('username', f"username = '{updates['username']}'", 'users'):
            return {
                "error": "This username is already taken!",
                "status": 409
            }

        if self.fetch_specific_user('id', f"id = {id}", 'users'):
            return self.base_model.update_item(pairs, f"id = {id}", 'users')
        else:
            return {
                "error": "User not found or does not exist!",
                "status": 404
            }    
        