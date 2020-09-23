"""Configuration for development"""
import os


DEV_DATABASE_URI = os.getenv("postgres://postgres:none@127.0.0.1:5432/zaobora_database")
DEV_SECRET_KEY = os.getenv('DEV_SECRET_KEY')
DEV_SECURITY_PASSWORD_SALT = os.getenv('DEV_SECURITY_PASSWORD_SALT')
DEV_MAIL_SERVER = os.getenv('DEV_MAIL_SERVER')
DEV_MAIL_PORT = os.getenv('DEV_MAIL_PORT')
DEV_MAIL_USE_TLS = os.getenv('DEV_MAIL_USE_TLS')
DEV_SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('DEV_SQLALCHEMY_TRACK_MODIFICATIONS')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')