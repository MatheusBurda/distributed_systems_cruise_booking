import time
import pika
from flask import current_app

class RabbitMQManager:
    _instance = None
    _connection = None
    _channel = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RabbitMQManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._connection:
            self._connection = self._create_connection()
            self._channel = self._connection.channel()
            self._setup_exchanges()

    def _create_connection(self):
        credentials = pika.PlainCredentials(
            current_app.config['RABBITMQ_USER'],
            current_app.config['RABBITMQ_PASS']
        )
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                host=current_app.config['RABBITMQ_HOST'],
                port=int(current_app.config['RABBITMQ_PORT']),
                credentials=credentials,
                heartbeat=3600
            )
        )

    def _setup_exchanges(self):
        self._channel.exchange_declare(exchange="direct", exchange_type="direct")

    @property
    def channel(self):
        while True:
            try:
                if not self._channel or self._channel.is_closed:
                    self._connection = self._create_connection()
                    self._channel = self._connection.channel()
                    self._setup_exchanges()
                break
            except Exception as e:
                print(f"Failed to establish connection: {e}")
                time.sleep(1)
        return self._channel


    def publish_payment_approved(self, message: str):
        self.channel.basic_publish(
            exchange="direct",
            routing_key=current_app.config["PAYMENT_ACCEPTED_ROUTING_KEY"],
            body=message.encode("utf-8"),
            properties=pika.BasicProperties(
                headers={"sender": "payments"},
                delivery_mode=2
            )
        )

    def publish_payment_rejected(self, message: str):
        self.channel.basic_publish(
            exchange="direct",
            routing_key=current_app.config["PAYMENT_REJECTED_ROUTING_KEY"],
            body=message.encode("utf-8"),
            properties=pika.BasicProperties(
                headers={"sender": "payments"},
                delivery_mode=2
            )
        )

