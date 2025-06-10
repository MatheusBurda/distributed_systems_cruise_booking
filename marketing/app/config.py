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
    MARKETING_ROUTING_KEY = os.getenv("MARKETING_ROUTING_KEY")

    MARKETING_API_PORT = os.getenv("MARKETING_API_PORT")

    @classmethod
    def validate(cls):
        required_vars = [
            cls.RABBITMQ_USER,
            cls.RABBITMQ_PASS,
            cls.RABBITMQ_HOST,
            cls.RABBITMQ_PORT,
            cls.LOGS_ROUTING_KEY,
            cls.MARKETING_ROUTING_KEY,
            cls.MARKETING_API_PORT
        ]
        if not all(required_vars):
            raise EnvironmentError("One or more required environment variables are missing.")