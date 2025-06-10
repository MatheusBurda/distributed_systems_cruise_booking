from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.core.rabbitmq import RabbitMQManager
from app.routes.create_promotion import promotions_bp

def create_app():
    app = Flask(__name__)
    CORS(app, origins="*")
    
    app.config.from_object(Config)
    Config.validate()
    
    app.register_blueprint(promotions_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        rabbitmq_manager = RabbitMQManager()
    
    print("Promotions service started")
    app.run(host="0.0.0.0", port=int(Config.MARKETING_API_PORT))
