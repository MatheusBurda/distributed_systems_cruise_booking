import json
import pika
import os
from random import randint
from dotenv import load_dotenv

from payment import accept_payment, reject_payment

load_dotenv()

##############################################################
#                ENVS and DEFAULT_VALUES
##############################################################
PERCENTAGE_ERROR = 50 # %

# RabbitMQ infos
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")

# Routing Keys
LOGS_ROUTING_KEY = os.getenv("LOGS_ROUTING_KEY")
PAYMENT_REJECTED_ROUTING_KEY=os.getenv("PAYMENT_REJECTED_ROUTING_KEY")
PAYMENT_ACCEPTED_ROUTING_KEY=os.getenv("PAYMENT_ACCEPTED_ROUTING_KEY")
RESERVATION_CREATED_ROUTING_KEY = os.getenv("RESERVATION_CREATED_ROUTING_KEY")

if not all([RABBITMQ_USER, RABBITMQ_PASS, RABBITMQ_HOST, RABBITMQ_PORT, RESERVATION_CREATED_ROUTING_KEY]):
    raise EnvironmentError("One or more required environment variables are missing.")
##############################################################

def callback(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))
    sender = properties.headers.get("sender", "unknown")

    channel.basic_publish(
        exchange="direct", 
        routing_key=LOGS_ROUTING_KEY, 
        body=f"Reservation Created Received".encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "payments"})
    )

    random_number = randint(0,100)

    if random_number < PERCENTAGE_ERROR: 
        return_data = reject_payment(data) 
        json_body = json.dumps(return_data)

        channel.basic_publish(
            exchange="direct", 
            routing_key=PAYMENT_REJECTED_ROUTING_KEY, 
            body=json_body.encode("utf-8"), 
            properties=pika.BasicProperties(headers={"sender": "payments"})
        )
        
    else: 
        return_data = accept_payment(data)
        json_body = json.dumps(return_data)

        channel.basic_publish(
            exchange="direct", 
            routing_key=PAYMENT_ACCEPTED_ROUTING_KEY, 
            body=json_body.encode("utf-8"), 
            properties=pika.BasicProperties(headers={"sender": "payments"})
        )

##############################################################
print("Starting payments service")

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=int(RABBITMQ_PORT), credentials=credentials))

channel = connection.channel()
channel.exchange_declare(exchange="direct", exchange_type="direct")

# Reservation Created Queue ->  consumer
queue_name = "reservation_created_queue_payments"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange="direct", queue=queue_name, routing_key=RESERVATION_CREATED_ROUTING_KEY)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("Finished setup. \nStart consuming...")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping payments service.")

##############################################################
