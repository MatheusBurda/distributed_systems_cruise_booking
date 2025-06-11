from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.core.rabbitmq import RabbitMQManager
from app.routes import payments_bp

def create_app():
    app = Flask(__name__)
    CORS(app, origins="*")
    
    app.config.from_object(Config)
    Config.validate()
    
    app.register_blueprint(payments_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        rabbitmq_manager = RabbitMQManager()
    
    print("Payments service started")
    app.run(host="0.0.0.0", port=int(Config.PAYMENT_MS_PORT))
