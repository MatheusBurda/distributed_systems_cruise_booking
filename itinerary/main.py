from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.core.data_manager import DataManager
from app.core.rabbitmq import RabbitMQManager
from app.routes.get_list import itineraries_bp

def create_app():
    app = Flask(__name__)
    CORS(app, origins="*")
    
    app.config.from_object(Config)
    Config.validate()
    
    app.register_blueprint(itineraries_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        data_manager = DataManager()
        rabbitmq_manager = RabbitMQManager()
    
    print("Itinerary service started")
    app.run(host="0.0.0.0", port=int(Config.ITINERARY_MS_PORT))
