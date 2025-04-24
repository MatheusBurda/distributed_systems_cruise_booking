import pika
import json
import os
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
PROMOTIONS_ROUTINGKEY = os.getenv("PROMOTIONS_ROUTINGKEY_NAME")

if not all([RABBITMQ_USER, RABBITMQ_PASS, RABBITMQ_HOST, RABBITMQ_PORT, PROMOTIONS_ROUTINGKEY]):
    raise EnvironmentError("One or more required environment variables are missing.")

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=int(RABBITMQ_PORT), credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue=PROMOTIONS_ROUTINGKEY, durable=True)

def callback(ch, method, properties, body):
    print(f"{body}")

channel.basic_consume(queue=PROMOTIONS_ROUTINGKEY, on_message_callback=callback, auto_ack=True)

try:
    print("Starting logging consuming...")
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping marketing service.")

    