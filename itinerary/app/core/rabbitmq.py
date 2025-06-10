import pika
import threading
import json
from flask import current_app
from app.core.data_manager import DataManager

class RabbitMQManager:
    _instance = None
    _connection = None
    _channel = None
    _consumer_thread = None
    _running = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RabbitMQManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._connection:
            self._connection = self._create_connection()
            self._channel = self._connection.channel()
            self._setup_exchanges()
            self._start_consumer_thread()

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
        self._setup_queues()

    def _setup_queues(self):
        # Booking Created Queue
        queue_name = "booking_created"
        self._channel.queue_declare(queue=queue_name, durable=True)
        self._channel.queue_bind(
            exchange="direct",
            queue=queue_name,
            routing_key=current_app.config['BOOKING_CREATED_ROUTINGKEY']
        )

        # Booking Cancelled Queue
        queue_name = "booking_cancelled"
        self._channel.queue_declare(queue=queue_name, durable=True)
        self._channel.queue_bind(
            exchange="direct",
            queue=queue_name,
            routing_key=current_app.config['BOOKING_CANCELLED_ROUTINGKEY']
        )

        print("Exchanges and queues setup complete")

    def _start_consumer_thread(self):
        if not self._consumer_thread:
            self._running = True
            self._consumer_thread = threading.Thread(target=self._consume_messages)
            self._consumer_thread.daemon = True
            self._consumer_thread.start()

    def _consume_messages(self):
        while self._running:
            try:
                if not self._channel or self._channel.is_closed:
                    self._connection = self._create_connection()
                    self._channel = self._connection.channel()
                    self._setup_exchanges()

                # Set up consumers for both queues
                self._channel.basic_consume(
                    queue="booking_created",
                    on_message_callback=self._handle_booking_created
                )
                self._channel.basic_consume(
                    queue="booking_cancelled",
                    on_message_callback=self._handle_booking_cancelled
                )

                self._channel.start_consuming()
            except Exception as e:
                print(f"Error in consumer thread: {e}")
                if self._connection and not self._connection.is_closed:
                    self._connection.close()

    def _handle_booking_created(self, ch, method, properties, body):
        try:
            print("Booking created received")
            data = json.loads(body)
            result = DataManager().register_booking(
                destination_id=data['destination_id'],
                cabins=data['number_of_cabins']
            )
            if result:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print("Booking created processed")
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag)
                print("Booking created not processed")
        except Exception as e:
            print(f"Error handling booking created: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

    def _handle_booking_cancelled(self, ch, method, properties, body):
        try:
            print("Booking cancelled received")
            data = json.loads(body)
            result = DataManager().register_cancellation(
                destination_id=data['destination_id'],
                cabins=data['number_of_cabins']
            )
            if result:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                print("Booking cancelled processed")
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag)
                print("Booking cancelled not processed")
        except Exception as e:
            print(f"Error handling booking cancelled: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

    @property
    def channel(self):
        if not self._channel or self._channel.is_closed:
            self._connection = self._create_connection()
            self._channel = self._connection.channel()
            self._setup_exchanges()
        return self._channel

    # def publish_message(self, routing_key: str, message: str, headers: dict = None):
    #     self.channel.basic_publish(
    #         exchange="direct",
    #         routing_key=routing_key,
    #         body=message.encode("utf-8"),
    #         properties=pika.BasicProperties(headers=headers or {})
    #     )

    def stop(self):
        self._running = False
        if self._connection and not self._connection.is_closed:
            self._connection.close()

