from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes import payment_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app, origins="*")
    
    app.register_blueprint(payment_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=Config.PAYMENT_API_PORT)