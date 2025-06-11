import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
    
    # Routing Keys
    PAYMENT_ACCEPTED_ROUTING_KEY = os.getenv("PAYMENT_ACCEPTED_ROUTING_KEY")
    PAYMENT_REJECTED_ROUTING_KEY = os.getenv("PAYMENT_REJECTED_ROUTING_KEY")
    
    # API port
    PAYMENT_MS_PORT = os.getenv("PAYMENT_MS_PORT")
    PAYMENT_API_PORT = os.getenv("PAYMENT_API_PORT")

    @classmethod
    def validate(cls):
        required_vars = [
            cls.RABBITMQ_USER,
            cls.RABBITMQ_PASS,
            cls.RABBITMQ_HOST,
            cls.RABBITMQ_PORT,
            cls.PAYMENT_ACCEPTED_ROUTING_KEY,
            cls.PAYMENT_REJECTED_ROUTING_KEY,
            cls.PAYMENT_MS_PORT,
            cls.PAYMENT_API_PORT
        ]
        if not all(required_vars):
            raise EnvironmentError("One or more required environment variables are missing.")