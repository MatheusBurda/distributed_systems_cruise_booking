import json
import pika
import os
from dotenv import load_dotenv

load_dotenv()

##############################################################
#                ENVS and DEFAULT_VALUES
##############################################################
PERCENTAGE_ERROR = 20 # %

# RabbitMQ infos
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")

# Routing Keys
LOGS_ROUTINGKEY = os.getenv("LOGS_ROUTINGKEY")

if not all([RABBITMQ_USER, RABBITMQ_PASS, RABBITMQ_HOST, RABBITMQ_PORT, LOGS_ROUTINGKEY]):
    raise EnvironmentError("One or more required environment variables are missing.")
##############################################################

def callback(ch, method, properties, body):
    data = body.decode("utf-8")
    sender = properties.headers.get("sender", "unknown")

    print(f"[{sender}]: {data}")


##############################################################
print("Starting logging service")

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=int(RABBITMQ_PORT), credentials=credentials))

channel = connection.channel()
channel.exchange_declare(exchange="direct", exchange_type="direct")

queue_name = "logger_queue"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange="direct", queue=queue_name, routing_key=LOGS_ROUTINGKEY)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("Finished setup. Start consuming...")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping logging service.")

##############################################################
