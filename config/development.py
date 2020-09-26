"""Configuration for development"""
import os
from datetime import timedelta


DATABASE_URI = os.getenv('DATABASE_URI')
SECRET_KEY = os.getenv('SECRET_KEY')
REDIS_URL = os.getenv('REDIS_URL')
SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES = timedelta(days=30)
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
