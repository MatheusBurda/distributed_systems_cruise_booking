from flask import Flask
from flask_cors import CORS

from app.config import Config
# from app.core.rabbitmq import RabbitMQManager
from app.routes.booking import bookings_bp
from app.routes.itinerary import itineraries_bp

def create_app():
    app = Flask(__name__)
    CORS(app, origins="*")
    
    app.config.from_object(Config)
    Config.validate()
    
    app.register_blueprint(bookings_bp)
    app.register_blueprint(itineraries_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    
    # with app.app_context():
    #     rabbitmq_manager = RabbitMQManager()
    
    print("Booking service started", Config.API_PORT, Config.ITINERARY_MS_PORT)
    app.run(host="0.0.0.0", port=int(Config.API_PORT))
