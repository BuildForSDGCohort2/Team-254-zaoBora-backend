import os
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
    CORS(app)

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
    redis_client = FlaskRedis(app)
    redis_client.init_app(app)

    # v1 Blueprints
    from app.api.v1.views.user_view import v1 as user_v1
    from app.api.v1.views.product_view import v1 as product_v1
    from app.api.v1.views.vendor_view import v1 as vendor_v1
    from app.api.v1.views.order_view import v1 as order_v1

    # Register blueprints
    app.register_blueprint(user_v1)
    app.register_blueprint(product_v1)
    app.register_blueprint(vendor_v1)
    app.register_blueprint(order_v1)

    # init Flask-Mail
    mail.init_app(app)

    # instantiate mpesa
    mpesaapi= MpesaAPI()

    #init mpesa api on app
    mpesaapi.init_app(app)
    
    # init db
    db = Initialize_DB(app)
    db.init_redis(redis_client)
    db.init_db(DATABASE_URI)
    db.create_tables()
    db.connection.commit

    # Check if token is blacklisted
    @jwt.token_in_blacklist_loader
    def check_if_token_is_revoked(decrypted_token):
        revoked_store = redis_client
        jti = decrypted_token['jti']
        entry = revoked_store.get(jti)

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

    # # Send email
    # @app.route("/api/v1/verify-email", methods=['POST'])
    # def verify_email():
    #     try:
    #         data = request.get_json()
    #         email = data['email']
    #         token = serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)
    #         msg = Message("Please confirm your email",
    #                     sender="zaobora@gmail.com",
    #                     recipients=[email])
    #         link = url_for('confirm_email', token=token, _external=True)
            
    #         msg.body = 'Follow this link {}'.format(link)
    #         mail.send(msg)
    #         return jsonify({
    #             "msg": "Email sent successfully"
    #         }), 200
    #     except:
    #         return jsonify({
    #             "error": "unable to send email"
    #         }), 400

    # # Verify email
    # @app.route('/api/v1/confirm_email/<token>')
    # def confirm_email(token):
    #     try:
    #         email = serializer.loads(token, salt=SECURITY_PASSWORD_SALT, max_age=3600)

    #         return jsonify({ "msg": "Email sent successfully" }), 200
    #     except SignatureExpired:
    #         return jsonify({ "error": "The token has expired!" }), 403
    #     except BadTimeSignature:
    #         return jsonify({ "error": "The token is invalid!" }), 403

    return app
