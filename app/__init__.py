import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import (JWTManager)
from flask_redis import FlaskRedis

from app.database import Initialize_DB
from flask_mpesa import MpesaAPI
from config.development import DATABASE_URI

def create_app(config_name):
    # func to initialize Flask app

    # init app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    # Load the default configuration
    app.config.from_object('config.default')

    # Load the development configuration
    app.config.from_object('config.development')

    # Load the configuration from the instance folder

    # Load configurations specified by the APP_CONFIG_FILE environment variable
    # Variables contained here will override those in the default configuration
    # export APP_CONFIG_FILE=/path/to/config/production.py
    app.config.from_envvar('APP_CONFIG_FILE')

    # init JWT
    jwt = JWTManager()
    jwt.init_app(app)

    # init Cache
    redis_client = FlaskRedis(app)
    redis_client.init_app(app)

    # v1 Blueprints
    from app.api.v1.views.user_view import v1 as user_v1
    from app.api.v1.views.product_view import v1 as product_v1
    from app.api.v1.views.vendor_view import v1 as vendor_v1
    from app.api.v1.views.order_view import v1 as order_v1

    app.register_blueprint(user_v1)

    # instantiate mpesa
    mpesaapi= MpesaAPI()
    app.register_blueprint(product_v1)
    app.register_blueprint(vendor_v1)

    #init mpesa api on app
    mpesaapi.init_app(app)
    # init db
    db = Initialize_DB(app)
    db.init_redis(redis_client)
    db.init_db(DATABASE_URI)
    db.create_tables()
    db.connection.commit

    @jwt.token_in_blacklist_loader
    def check_if_token_is_revoked(decrypted_token):
        revoked_store = redis_client
        jti = decrypted_token['jti']
        entry = revoked_store.get(jti).decode()
        print(entry)

        if entry is None:
            return True
        return entry == 'true'

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
