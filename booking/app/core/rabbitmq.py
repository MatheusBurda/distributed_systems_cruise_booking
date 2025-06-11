import base64
import json
import pika
import threading

from app.config import config
from app.services.marketing_manager import MarketingManager
from app.core.crypto_verify import verify_signature
from app.services.booking_manager import BookingsManager

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
            self._setup()
            self._start_consumer_thread()

    def _create_connection(self):
        credentials = pika.PlainCredentials(
            config.RABBITMQ_USER,
            config.RABBITMQ_PASS
        )
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                port=int(config.RABBITMQ_PORT),
                credentials=credentials,
                heartbeat=3600
            )
        )

    def _setup(self):
        self._channel.exchange_declare(exchange="direct", exchange_type="direct")
        self._channel.exchange_declare(exchange="promotions_topic", exchange_type="topic")

        # Payment Accepted Queue ->  consumer
        queue_name = "payment_approved"
        self._channel.queue_declare(queue=queue_name, durable=True)
        self._channel.queue_bind(exchange="direct", queue=queue_name, routing_key=config.PAYMENT_ACCEPTED_ROUTING_KEY)

        # Payment Rejected Queue ->  consumer
        queue_name = "payment_rejected"
        self._channel.queue_declare(queue=queue_name, durable=True)
        self._channel.queue_bind(exchange="direct", queue=queue_name, routing_key=config.PAYMENT_REJECTED_ROUTING_KEY)

        # Ticket Generated Queue ->  consumer
        queue_name = "ticket_generated"
        self._channel.queue_declare(queue=queue_name, durable=True)
        self._channel.queue_bind(exchange="direct", queue=queue_name, routing_key=config.TICKET_GENERATED_ROUTING_KEY)

        # Promotion Queue ->  consumer
        queue_name = "promotions"
        self._channel.queue_declare(queue=queue_name, durable=True)
        self._channel.queue_bind(exchange="promotions_topic", queue=queue_name, routing_key=str(config.MARKETING_ROUTING_KEY) + f".#")

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
                    self._setup()

                # Set up consumers for queues
                self._channel.basic_consume(
                    queue="payment_approved", 
                    on_message_callback=self._handle_payment_approved, 
                    auto_ack=True
                )
                self._channel.basic_consume(
                    queue="payment_rejected", 
                    on_message_callback=self._handle_payment_rejected, 
                    auto_ack=True
                )
                self._channel.basic_consume(
                    queue="ticket_generated", 
                    on_message_callback=self._handle_ticket_generated, 
                    auto_ack=True
                )
                self._channel.basic_consume(
                    queue="promotions", 
                    on_message_callback=self._handle_promotion, 
                    auto_ack=True
                )

                self._channel.start_consuming()
            except Exception as e:
                print(f"Error in consumer thread: {e}")
                if self._connection and not self._connection.is_closed:
                    self._connection.close()

    def _handle_payment_approved(self, ch, method, properties, body):
        data = json.loads(body.decode("utf-8"))

        self.publish_log("Payment Accepted Received", headers={"sender": "booking"})

        signature = base64.b64decode(data["signature"])
        transaction = data["transaction"]
        transaction_str = json.dumps(transaction, sort_keys=True)

        if not verify_signature(value=transaction_str, sig=signature):
            self.publish_log(f"ERROR: Payment accepted - signature invalid! transaction_id: {transaction['id']} for reservation_id {transaction['reservation_id']}", headers={"sender": "booking"})
            return

        booking_manager = BookingsManager()
        booking_manager.register_payment_accepted(transaction["reservation_id"], transaction["id"])

    def _handle_payment_rejected(self, ch, method, properties, body):
        data = json.loads(body.decode("utf-8"))

        self.publish_log("Payment Rejected Received", headers={"sender": "booking"})

        signature = base64.b64decode(data["signature"])
        transaction = data["transaction"]
        transaction_str = json.dumps(transaction, sort_keys=True)

        if not verify_signature(value=transaction_str, sig=signature):
            self.publish_log(f"ERROR: Payment rejected signature invalid! transaction_id: {transaction['id']} for reservation_id {transaction['reservation_id']}", headers={"sender": "booking"})
            return

        booking_manager = BookingsManager()
        booking_manager.register_payment_rejected(transaction["reservation_id"], transaction["id"])

    def _handle_ticket_generated(self, ch, method, properties, body):
        data = json.loads(body.decode("utf-8"))

        booking_manager = BookingsManager()
        booking_manager.register_ticket_generated(data["reservation_id"], data["tickets"])

    def _handle_promotion(self, ch, method, properties, body):
        notified = MarketingManager().notify_all(body)
        self.publish_log(message=f"Promotion Received and emmitted {notified} notifications")

    @property
    def channel(self):
        if not self._channel or self._channel.is_closed:
            self._connection = self._create_connection()
            self._channel = self._connection.channel()
            self._setup()
        return self._channel

    def _publish_message(self, routing_key: str, message: str, headers: dict = {"sender": "booking"}):
        try:
            self.channel.basic_publish(
                exchange="direct",
                routing_key=routing_key,
                body=message.encode("utf-8"),
                properties=pika.BasicProperties(headers=headers)
            )
        except Exception as e:
            print(f"Error publishing message: {e}")


    def publish_booking_created(self, message: str):
        self._publish_message(config.BOOKING_CREATED_ROUTING_KEY, message, {"sender": "booking"})
    
    def publish_booking_cancelled(self, message: str):
        self._publish_message(config.BOOKING_CANCELLED_ROUTING_KEY, message, {"sender": "booking"})

    def publish_log(self, message: str, headers: dict = {"sender": "booking"}):
        try: 
            self.channel.basic_publish(
                exchange="direct",
                routing_key=config.LOGS_ROUTING_KEY,
                body=message.encode("utf-8"),
                properties=pika.BasicProperties(headers=headers)
            )
        except Exception as e:
            print(f"Error publishing log message: {e}")

    def stop(self):
        self._running = False
        if self._connection and not self._connection.is_closed:
            self._connection.close()

