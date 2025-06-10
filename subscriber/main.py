import os
import json
import pika
from dotenv import load_dotenv

load_dotenv()

##############################################################
#                ENVS and DEFAULT_VALUES
##############################################################
# RabbitMQ infos
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")

# Routing Keys
LOGS_ROUTING_KEY = os.getenv("LOGS_ROUTING_KEY")
MARKETING_ROUTING_KEY=os.getenv("MARKETING_ROUTING_KEY")

if not all([
    RABBITMQ_USER, 
    RABBITMQ_PASS, 
    RABBITMQ_HOST, 
    RABBITMQ_PORT, 
    MARKETING_ROUTING_KEY, 
    LOGS_ROUTING_KEY, 
    ]):
    raise EnvironmentError("One or more required environment variables are missing.")

##############################################################
#                           CALLBACKS
##############################################################

def callback(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))
    routing_key = method.routing_key

    print(f'Received a new promotion on queue with routing key [{routing_key}]:\n{data}')

##############################################################
#          QUEUES DECLARATION and RABBITMQ SETUP
##############################################################
print("Starting subscriber service")

def create_rabbitmq_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST, 
            port=int(RABBITMQ_PORT), 
            credentials=credentials,
            heartbeat=3600
        )
    )
    return connection

# Create connection and channel for the consumer
connection = create_rabbitmq_connection()
channel = connection.channel()
channel.exchange_declare(exchange="promotions_topic", exchange_type="topic")

# Subscriber Queue to receive promotions from destination with id 7
queue_name = "subscriber_queue_destination_id_7"
routing_key = str(MARKETING_ROUTING_KEY) + f".7"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange="promotions_topic", queue=queue_name, routing_key=routing_key)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print(f"Queue {queue_name} subscribed to {routing_key}")

# Subscriber Queue to receive promotions from destination with id 22
queue_name = "subscriber_queue_destination_id_22"
routing_key = str(MARKETING_ROUTING_KEY) + f".22"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange="promotions_topic", queue=queue_name, routing_key=routing_key)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print(f"Queue {queue_name} subscribed to {routing_key}")

# Subscriber Queue to receive promotions from all destinations 
queue_name = "subscriber_queue_destination_all"
routing_key = str(MARKETING_ROUTING_KEY) + f".#"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange="promotions_topic", queue=queue_name, routing_key=routing_key)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print(f"Queue {queue_name} subscribed to {routing_key}")

print("Finished setup. All queues declared")

##############################################################
#                     START SERVICES
##############################################################

def start_rabbitmq_consumer():
    "Start consuming RabbitMQ messages"
    print("Start consuming...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping reservation service.")
    finally:
        if connection and not connection.is_closed:
            connection.close()

if __name__ == "__main__":  
    start_rabbitmq_consumer()

##############################################################
