"""
This module performs all the database operations for the app
"""
import os
import jwt
import datetime
from functools import wraps, update_wrapper
from flask import jsonify, request, session

from app import create_app
from app.database import Initialize_DB

class BaseModel(Initialize_DB):
    # Base Model class for objects

    def __init__(self):
        # initializes list of object type
        self.table_name = ''

    @classmethod
    def encode_auth_token(cls, user_id):
        # generates authentication token

        app = create_app(cls.env)

        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    def blacklisted(self, details):
        # black lists tokens
        self.add_item('username, tokens', details, 'blacklist')

    def blacklisted(self, token):
        # checks whether a token blacklisted
        query = "SELECT id FROM blacklist WHERE tokens = '{}';".format(token)
        self.cursor.execute(query)
        if self.cursor.fetchone():
            return True
        return False

    @classmethod
    def decode_auth_token(cls, auth_token):
        # takes in token and decodes it

        app = create_app()

        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again!'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again!'

    def grab_all_items(self, cols, condition, name=''):
        # fetches all items
        name = name if name else self.table_name

        return self.fetch_all(
            "SELECT {} FROM {} WHERE {};".format(cols, name, condition)
        )

    def grab_items_by_name(self, cols, condition, name=''):
        # fetches an item by name
        name = name if name else self.table_name
      
        return self.fetch_one(
            "SELECT {} FROM {} WHERE {}".format(cols, name, condition)
        )

    def grab_items(self, column, condition, name=''):
        # fetches items by name
        name = name if name else self.table_name

        return self.fetch_one(
            "SELECT row_to_json({}) FROM {} WHERE {}".format(
                column, name, condition)
        )

    def add_item(self, keys, values, name=''):
        # adds an item
        name = name if name else self.table_name

        return self.execute(
            "INSERT INTO {} ({}) VALUES {}".format(name, keys, values)
        )

    def delete_item(self, condition, name=''):
        # defines the delete item query
        name = name if name else self.table_name

        return self.update(
            "DELETE FROM {} WHERE {}".format(name, condition)
        )

    def update_item(self, updates, condition, name=''):
        # defines the update item query
        name = name if name else self.table_name

        return self.update(
            "UPDATE {} SET {} WHERE {}".format(name, updates, condition)
        )

class AuthenticationRequired:
    # decorator class validates the token

    def __init__(self, f):
        self.f = f
        update_wrapper(self, f)

    def __call__(self, *args, **kwargs):
        auth_header = request.headers.get('Authorization')

        print(session)

        if not auth_header or len(auth_header) < 8 or " " not in auth_header:
            return jsonify({"error": "Please log in first...!"}), 403

        auth_token = auth_header.split(" ")[1]

        if isinstance(BaseModel().decode_auth_token(auth_token), str):
            return jsonify({"error": BaseModel().decode_auth_token(auth_token)}), 401

        return self.f(*args, **kwargs)
