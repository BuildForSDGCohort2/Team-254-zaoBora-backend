import os
import redis
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (JWTManager)
from flask_redis import FlaskRedis
from flask_mail import Mail
from flask_mail import Message

from app.database import Initialize_DB
from flask_mpesa import MpesaAPI
from config.development import DATABASE_URI
from app.api.v1.utils.email import mail


def create_app(config_name):
    # func to initialize Flask app

    # init app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load the default configuration
    app.config.from_object('config.default')

    # Load the development configuration
    app.config.from_object('config.development')

    # Load the configuration from the instance folder

    # Load configurations specified by the APP_CONFIG_FILE environment variable
    # Variables contained here will override those in the default configuration
    # export APP_CONFIG_FILE=/path/to/config/production.py

    # init JWT
    jwt = JWTManager()
    jwt.init_app(app)

    # init Cache
    redis_store = redis.StrictRedis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=0,
        password=app.config['REDIS_PASS'],
        connection_pool=None,
        decode_responses=True
    )

    # v1 Blueprints
    from app.api.v1.views.user_view import v1 as user_v1
    from app.api.v1.views.product_view import v1 as product_v1
    from app.api.v1.views.vendor_view import v1 as vendor_v1
    from app.api.v1.views.order_view import v1 as order_v1
    from app.api.v1.views.cart_view import v1 as cart_v1
    from app.api.v1.views.review_view import v1 as review_v1
    from app.api.v1.views.receipt_view import v1 as receipt_v1

    # Register blueprints
    app.register_blueprint(user_v1)
    app.register_blueprint(product_v1)
    app.register_blueprint(vendor_v1)
    app.register_blueprint(order_v1)
    app.register_blueprint(review_v1)
    app.register_blueprint(cart_v1)
    app.register_blueprint(receipt_v1)

    # init Flask-Mail
    mail.init_app(app)

    # instantiate mpesa
    mpesaapi= MpesaAPI()

    #init mpesa api on app
    mpesaapi.init_app(app)
    
    # init db
    db = Initialize_DB(app)
    db.init_redis(redis_store)
    db.init_db(DATABASE_URI)
    db.create_tables()
    db.connection.commit

    # Check if token is blacklisted
    @jwt.token_in_blacklist_loader
    def check_if_token_is_revoked(decrypted_token):
        revoked_store = redis_store
        jti = decrypted_token['jti']
        entry = revoked_store.get(jti)

        if entry is None:
            return True
        return entry == 'true'
    
    @app.after_request
    def after_request(response):
        url = request.referrer[:-1]
        print('url: ',url)
        white_list = ['https://zaobora-frontend.herokuapp.com', 'http://localhost:8080']

        if url in white_list:
            response.headers.add('Access-Control-Allow-Origin', )
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH')
            response.headers.add('Access-Control-Allow-Credentials', 'true')

        return response

    @app.route('/')
    @app.route('/index')
    @app.route('/api/v1')
    def index():
        # endpoint for the landing page

        return jsonify({'status': 200, 'message': 'Welcome to ZaoBora'})

    @app.errorhandler(404)
    def page_not_found(error):
        # handler for error 404

        return jsonify({'status': 404, 'message': 'Oops! The requested page was not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        # handler for error 405

        return jsonify({'status': 405, 'message': 'Method not allowed'}), 405

    return app
