from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes import payment_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app)
    
    app.register_blueprint(payment_bp)
    
    return app