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
    PAYMENT_ACCEPTED_ROUTING_KEY = os.getenv("PAYMENT_ACCEPTED_ROUTING_KEY")
    PAYMENT_REJECTED_ROUTING_KEY = os.getenv("PAYMENT_REJECTED_ROUTING_KEY")
    TICKET_GENERATED_ROUTING_KEY = os.getenv("TICKET_GENERATED_ROUTING_KEY")
    MARKETING_ROUTING_KEY = os.getenv("MARKETING_ROUTING_KEY")
    BOOKING_CREATED_ROUTING_KEY = os.getenv("BOOKING_CREATED_ROUTING_KEY")
    BOOKING_CANCELLED_ROUTING_KEY = os.getenv("BOOKING_CANCELLED_ROUTING_KEY")

    # API Keys
    ITINERARY_MS_PORT = os.getenv("ITINERARY_MS_PORT")
    PAYMENT_MS_PORT = os.getenv("PAYMENT_MS_PORT")
    API_PORT = os.getenv("API_PORT")

    @classmethod
    def validate(cls):
        required_vars = [
            cls.RABBITMQ_USER,
            cls.RABBITMQ_PASS,
            cls.RABBITMQ_HOST,
            cls.RABBITMQ_PORT,
            cls.LOGS_ROUTING_KEY,
            cls.PAYMENT_ACCEPTED_ROUTING_KEY,
            cls.PAYMENT_REJECTED_ROUTING_KEY,
            cls.TICKET_GENERATED_ROUTING_KEY,
            cls.MARKETING_ROUTING_KEY,
            cls.ITINERARY_MS_PORT,
            cls.PAYMENT_MS_PORT,
            cls.API_PORT,
            cls.BOOKING_CREATED_ROUTING_KEY,
            cls.BOOKING_CANCELLED_ROUTING_KEY
        ]
        if not all(required_vars):
            raise EnvironmentError("One or more required environment variables are missing.")
        
config = Config()