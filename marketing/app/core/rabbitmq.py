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
        self._channel.exchange_declare(exchange="promotions_topic", exchange_type="topic")

    @property
    def channel(self):
        if not self._channel or self._channel.is_closed:
            self._connection = self._create_connection()
            self._channel = self._connection.channel()
            self._setup_exchanges()
        return self._channel

    def publish_promotion(self, routing_key: str, message: str, headers: dict = None):
        self.channel.basic_publish(
            exchange="promotions_topic",
            routing_key=routing_key,
            body=message.encode("utf-8"),
            properties=pika.BasicProperties(headers=headers or {})
        )

