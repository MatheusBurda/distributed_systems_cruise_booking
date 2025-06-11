import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
    
    # Routing Keys
    LOGS_ROUTING_KEY = os.getenv("LOGS_ROUTING_KEY")
    BOOKING_CREATED_ROUTING_KEY = os.getenv("BOOKING_CREATED_ROUTING_KEY")
    BOOKING_CANCELLED_ROUTING_KEY = os.getenv("BOOKING_CANCELLED_ROUTING_KEY")

    # API Keys
    ITINERARY_MS_PORT = os.getenv("ITINERARY_MS_PORT")
    PAYMENT_MS_PORT = os.getenv("PAYMENT_MS_PORT")

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123')
    PAYMENT_WEBHOOK_URL = os.getenv('PAYMENT_WEBHOOK_URL', f'http://payments:{PAYMENT_MS_PORT}/webhook')
    PAYMENT_SUCCESS_RATE = float(os.getenv('PAYMENT_SUCCESS_RATE', '0.8'))  # 80% success rate by default

    @classmethod
    def validate(cls):
        required_vars = [
            cls.RABBITMQ_USER,
            cls.RABBITMQ_PASS,
            cls.RABBITMQ_HOST,
            cls.RABBITMQ_PORT,
            cls.LOGS_ROUTING_KEY,
            cls.BOOKING_CREATED_ROUTING_KEY,
            cls.BOOKING_CANCELLED_ROUTING_KEY,
            cls.ITINERARY_MS_PORT
        ]
        if not all(required_vars):
            raise EnvironmentError("One or more required environment variables are missing.")