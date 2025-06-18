import base64
import json
import time
import pika
import threading

from app.config import config
from app.services.marketing_manager import MarketingManager
from app.core.crypto_verify import verify_signature
from app.services.booking_manager import BookingsManager
from app.models.payment import Payment

class RabbitMQManager:
    _instance = None
    _connection = None
    _channel = None
    _consumer_thread = None
    _running = False
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RabbitMQManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._connection = self._create_connection()
                    self._channel = self._connection.channel()
                    self._setup()
                    self._start_consumer_thread()
                    self._initialized = True


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
                heartbeat=60 
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

    def _reconnect_if_needed(self):
        if not self._connection or self._connection.is_closed or not self._channel or self._channel.is_closed:
            print("Connection lost. Reconnecting...")
            try:
                self._connection = self._create_connection()
                self._channel = self._connection.channel()
                self._setup()
                print("Reconnection successful.")
            except Exception as e:
                print(f"Failed to reconnect: {e}")
                if self._connection and not self._connection.is_closed:
                    self._connection.close()
                self._connection = None
                self._channel = None
                return False
        return True

    def _consume_messages(self):
        print("Consumer thread started.")
        queues = ["payment_approved", "payment_rejected", "ticket_generated", "promotions"]
        handlers = {
            "payment_approved": self._handle_payment_approved,
            "payment_rejected": self._handle_payment_rejected,
            "ticket_generated": self._handle_ticket_generated,
            "promotions": self._handle_promotion
        }

        while self._running:
            try:
                with self._lock:
                    if not self._reconnect_if_needed():
                        time.sleep(5)
                        continue

                    for queue_name in queues:
                        method_frame, header_frame, body = self._channel.basic_get(queue=queue_name, auto_ack=True)
                        if method_frame:
                            handler = handlers.get(queue_name)
                            if handler:
                                try:
                                    handler(self._channel, method_frame, header_frame, body)
                                except Exception as handler_e:
                                    print(f"Error handling message from {queue_name}: {handler_e}")
                
                time.sleep(0.1)

            except Exception as e:
                print(f"Error in consumer thread loop: {e}")
                time.sleep(5)
    
    def _handle_payment_approved(self, ch, method, properties, body):
        data = json.loads(body.decode("utf-8"))
        self.publish_log("Payment Accepted Received", headers={"sender": "booking"})
        signature = base64.b64decode(data["signature"])
        transaction = data["transaction"]
        transaction_str = json.dumps(transaction, sort_keys=True)
        if not verify_signature(value=transaction_str, sig=signature):
            self.publish_log(f"ERROR: Payment accepted - signature invalid! transaction_id: {transaction['id']} for booking_id {transaction['booking_id']}", headers={"sender": "booking"})
            return
        booking_manager = BookingsManager()
        payment = Payment.from_dict(transaction)
        booking_manager.register_payment_accepted(transaction["booking_id"], payment)


    def _handle_payment_rejected(self, ch, method, properties, body):
        data = json.loads(body.decode("utf-8"))
        self.publish_log("Payment Rejected Received", headers={"sender": "booking"})
        signature = base64.b64decode(data["signature"])
        transaction = data["transaction"]
        transaction_str = json.dumps(transaction, sort_keys=True)
        if not verify_signature(value=transaction_str, sig=signature):
            self.publish_log(f"ERROR: Payment rejected signature invalid! transaction_id: {transaction['id']} for booking_id {transaction['booking_id']}", headers={"sender": "booking"})
            return
        booking_manager = BookingsManager()
        payment = Payment.from_dict(transaction)
        booking_manager.register_payment_rejected(transaction["booking_id"], payment)

    def _handle_ticket_generated(self, ch, method, properties, body):
        data = json.loads(body.decode("utf-8"))
        booking_manager = BookingsManager()
        booking_manager.register_ticket_generated(data["booking_id"], data["tickets"])

    def _handle_promotion(self, ch, method, properties, body):
        notified = MarketingManager().notify_all(body)
        self.publish_log(message=f"Promotion Received and emmitted {notified} notifications")


    def _publish_message(self, exchange: str, routing_key: str, message: str, headers: dict = {"sender": "booking"}):
        with self._lock:
            try:
                if not self._reconnect_if_needed():
                    print("Error: Could not publish message, no connection available.")
                    return

                self._channel.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=message.encode("utf-8"),
                    properties=pika.BasicProperties(headers=headers)
                )
            except Exception as e:
                print(f"Error publishing message: {e}")

                if self._connection and not self._connection.is_closed:
                    self._connection.close()

    def publish_booking_created(self, message: str):
        self._publish_message("direct", config.BOOKING_CREATED_ROUTING_KEY, message, {"sender": "booking"})
    
    def publish_booking_cancelled(self, message: str):
        self._publish_message("direct", config.BOOKING_CANCELLED_ROUTING_KEY, message, {"sender": "booking"})

    def publish_log(self, message: str, headers: dict = {"sender": "booking"}):
        self._publish_message("direct", config.LOGS_ROUTING_KEY, message, headers)

    def stop(self):
        print("Stopping RabbitMQ Manager...")
        self._running = False
        if self._consumer_thread:
            self._consumer_thread.join()
            self._consumer_thread = None

        with self._lock:
            if self._channel and self._channel.is_open:
                self._channel.close()
            if self._connection and self._connection.is_open:
                self._connection.close()
        print("RabbitMQ Manager stopped.")