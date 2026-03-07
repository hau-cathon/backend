"""Flask extensions initialization"""
from mongoengine import connect
from flask_jwt_extended import JWTManager
from flask_cors import CORS

jwt = JWTManager()
cors = CORS()

def init_db(app):
    """Initialize MongoDB connection"""
    mongodb_uri = app.config['MONGODB_URI']
    mongodb_db = app.config['MONGODB_DB']
    connect(mongodb_db, host=mongodb_uri)
