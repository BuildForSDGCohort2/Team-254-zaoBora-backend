import os

DEBUG = True
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USE_SSL = os.getenv('MAIL_USE_SSL')
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
# CORS_HEADERS = "Content-Type"
# CORS_RESOURCES = {r"/api/*": {"origins": "*"}}
# CORS_SUPPORTS_CREDENTIALS = True
