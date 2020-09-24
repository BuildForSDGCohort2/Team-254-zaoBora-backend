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
from config.development import SECRET_KEY


class BaseModel(Initialize_DB):
    # Base Model class for objects

    def __init__(self):
        # initializes list of object type
        self.table_name = ''
        self.cache = self.redis_client

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