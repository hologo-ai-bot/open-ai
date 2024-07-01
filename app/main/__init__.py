from flask import Flask
from flask_mongoengine import MongoEngine
# from flask_socketio import SocketIO
from .controllers.openai_controller import openai_blueprint
from .controllers.client_controller import client_blueprint 

from .config import Config

db = MongoEngine()

def create_app():
    app = Flask(__name__)

    # Loading configuration
    app.config.from_object(Config)
    
    # Initialize MongoDB
    db.init_app(app)

    app.register_blueprint(openai_blueprint, url_prefix='/bot')
    app.register_blueprint(client_blueprint, url_prefix='/client')

    

    # socketio = SocketIO(app, cors_allowed_origins="*")

    return app
