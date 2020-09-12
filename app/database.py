import psycopg2
import os

class Initialize_DB:

    @classmethod
    def __init__(cls, db_url):
        cls.env = db_url.ENV

    @classmethod
    def init_db(cls, db_url):
        try:
            cls.connection = psycopg2.connect(db_url.SQLALCHEMY_DATABASE_URI)
            cls.cursor = cls.connection.cursor()
            print(f'A connection to {db_url.SQLALCHEMY_DATABASE_URI} database was established!')
        except:
            print(f'A problem occured while connecting to {db_url.SQLALCHEMY_DATABASE_URI}')

    @classmethod
    def create_tables(cls):

        cls.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id serial PRIMARY KEY NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                registered_on TIMESTAMP DEFAULT current_timestamp,
                modified_on TIMESTAMP DEFAULT current_timestamp 
            );
            
            CREATE TABLE IF NOT EXISTS vendors (
                id serial PRIMARY KEY NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                registered_on TIMESTAMP DEFAULT current_timestamp,
                modified_on TIMESTAMP DEFAULT current_timestamp 
            );
            
            CREATE TABLE IF NOT EXISTS products (
                id serial PRIMARY KEY NOT NULL,
                vendor_id INT REFERENCES vendors(id)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                product_name TEXT NOT NULL,
                description TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                regular_price INTEGER NOT NULL,
                discounted_price INTEGER NOT NULL,
                product_rating INTEGER NOT NULL,
                product_review TEXT NOT NULL,
                created_on TIMESTAMP DEFAULT current_timestamp   
            );
            
            CREATE TABLE IF NOT EXISTS categories (
                id serial PRIMARY KEY NOT NULL,
                category_name TEXT NOT NULL,
                category_description TEXT NOT NULL   
            );
            
            CREATE TABLE IF NOT EXISTS orders (
                id serial PRIMARY KEY NOT NULL,
                order_date TIMESTAMP DEFAULT current_timestamp,
                total_price INTEGER NOT NULL,
                order_status INTEGER NULL,
                tracking_number TEXT NOT NULL,
                buyer_id INT REFERENCES users(id)\
                ON UPDATE CASCADE ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS cart (
                id serial PRIMARY KEY NOT NULL,
                buyer_id INT REFERENCES users(id)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                productid INT REFERENCES products(id)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                quantity INTEGER NOT NULL                                   
            );
            
            CREATE TABLE IF NOT EXISTS blacklist(
                id serial PRIMARY KEY NOT NULL,
                username VARCHAR REFERENCES vendors(username)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                tokens VARCHAR NOT NULL
            );
                                       
            """
        )

        cls.connection.commit()

    @classmethod
    def execute(cls, query):
        # saves values into the db
        
        cls.cursor.execute(query)
        cls.connection.commit()

    @classmethod
    def fetch_all(cls, query):
        # fetches all items

        cls.cursor.execute(query)
        return cls.cursor.fetchall()

    @classmethod
    def fetch_one(cls, query):
        # fetches a single item

        cls.cursor.execute(query)
        return cls.cursor.fetchone()

    @classmethod
    def update(cls, query):
        # executes update queries

        cls.cursor.execute(query)
        cls.connection.commit()

    @classmethod
    def drop_tables(cls):
        # drops all tables

        cls.cursor.excute("DROP TABLE IF EXISTS users, products CASCADE;")
        cls.connection.commit()
