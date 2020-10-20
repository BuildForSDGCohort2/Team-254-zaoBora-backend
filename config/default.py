import os

DEBUG = True
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USE_SSL = os.getenv('MAIL_USE_SSL')
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASS = os.getenv('REDIS_PASS')
REDIS_HOST = os.getenv('REDIS_HOST')
CORS_HEADERS = 'Content-Type'
