import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import (JWTManager)

from instance.config import app_config
from app.database import Initialize_DB
from flask_mpesa import MpesaAPI






def create_app(config_name):
    # func to initialize Flask app

    # init app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    #app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    # init JWT
    jwt = JWTManager()
    jwt.init_app(app)

    # v1 Blueprints
    from app.api.v1.views.user_view import v1 as user_v1

    app.register_blueprint(user_v1)
    # instantiate mpesa
    mpesaapi= MpesaAPI()

    #init mpesa api on app
    mpesaapi.init_app(app)
    # init db
    db = Initialize_DB(app)
    #db.init_db(app)
    #db.create_tables()
    #db.connection.commit

    # @jwt.token_in_blacklist_loader
    # def check_blacklisted(token):
    #     from app.api.v1.models.token_model import RevokedTokenModel
    #     jti = token['jti']
    #     return RevokedTokenModel().is_blacklisted(jti)

    @app.route('/')
    @app.route('/index')
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
    #@v1.route('/transact/c2b')

    return app
