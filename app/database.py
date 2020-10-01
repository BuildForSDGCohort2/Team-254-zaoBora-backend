import psycopg2
import os

class Initialize_DB:

    @classmethod
    def __init__(cls, db_url):
        cls.env = db_url.env
        cls.redis_client = None
        cls.mail = None

    @classmethod
    def init_db(cls, db_url):
        try:
            cls.connection = psycopg2.connect(db_url)
            cls.cursor = cls.connection.cursor()
            print(f'A connection to {db_url} database was established!')
        except:
            print(f'A problem occured while connecting to {db_url}')

    @classmethod
    def init_redis(cls, redis_client):
        # Initialize redis_client
        cls.redis_client = redis_client

    @classmethod
    def init_mail(cls, mail):
        # Initialize mail
        cls.mail = mail

    @classmethod
    def create_tables(cls):

        cls.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id serial PRIMARY KEY NOT NULL,
                first_name CHAR(50) NOT NULL,
                last_name CHAR(50) NOT NULL,
                email CHAR(255) UNIQUE NOT NULL,
                username CHAR(50) UNIQUE NOT NULL,
                phone_number CHAR(50) NOT NULL,
                password CHAR(255) NOT NULL,
                is_farmer BOOLEAN NOT NULL,
                address TEXT,
                region CHAR(20),
                city CHAR(20),
                street_address CHAR(20),
                email_confirmed BOOLEAN DEFAULT false,
                registered_on TIMESTAMP DEFAULT current_timestamp,
                updated_on TIMESTAMP DEFAULT current_timestamp
            );

            CREATE TABLE IF NOT EXISTS vendors (
                id serial PRIMARY KEY NOT NULL,
                first_name CHAR(50) NOT NULL,
                last_name CHAR(50) NOT NULL,
                email CHAR(255) UNIQUE NOT NULL,
                username CHAR(50) UNIQUE NOT NULL,
                phone_number CHAR(50) NOT NULL,
                password CHAR(255) NOT NULL,
                address TEXT,
                region CHAR(20),
                city CHAR(20),
                street_address CHAR(20),
                email_confirmed BOOLEAN DEFAULT false,
                registered_on TIMESTAMP DEFAULT current_timestamp,
                updated_on TIMESTAMP DEFAULT current_timestamp
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
                mass CHAR(20) NOT NULL,
                created_on TIMESTAMP DEFAULT current_timestamp,
                updated_on TIMESTAMP DEFAULT current_timestamp
            );

            CREATE TABLE IF NOT EXISTS cart (
                id serial PRIMARY KEY NOT NULL,
                customer_id INT REFERENCES users(id)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                product_id INT REFERENCES products(id)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                quantity INTEGER NOT NULL,
                unit_price INTEGER NOT NULL,
                total INTEGER NOT NULL,
                created_on TIMESTAMP DEFAULT current_timestamp,
                updated_on TIMESTAMP DEFAULT current_timestamp
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id serial PRIMARY KEY NOT NULL,
                user_id INT REFERENCES users(id)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                product_id INT REFERENCES products(id)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                product_rating INT NOT NULL,
                review TEXT NOT NULL,
                created_on TIMESTAMP DEFAULT current_timestamp,
                updated_on TIMESTAMP DEFAULT current_timestamp
            );

            CREATE TABLE IF NOT EXISTS orders (
                id serial PRIMARY KEY NOT NULL,
                customer_id INT REFERENCES users(id)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                tracking_id CHAR(100) UNIQUE NOT NULL,
                items TEXT NOT NULL,
                status CHAR(20) DEFAULT 'pending' NOT NULL,
                total INTEGER NOT NULL,
                created_on TIMESTAMP DEFAULT current_timestamp,
                updated_on TIMESTAMP DEFAULT current_timestamp
            );

            CREATE TABLE IF NOT EXISTS receipts (
                id serial PRIMARY KEY NOT NULL,
                customer_id INT REFERENCES users(id)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                order_id INT REFERENCES orders(id)\
                ON UPDATE CASCADE ON DELETE CASCADE,
                discount INT DEFAULT 0,
                delivery_fee INT DEFAULT 0,
                subtotal INTEGER NOT NULL,
                total INTEGER NOT NULL,
                created_on TIMESTAMP DEFAULT current_timestamp,
                updated_on TIMESTAMP DEFAULT current_timestamp
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


# -- JOIN query example
# SELECT u.name, b.id, b.base_name
# FROM users AS u
# INNER JOIN base_table AS b
# ON u.base_id = b.id
# WHERE b.base_name = 'Nairobi';