import base64
import os
import json
import uuid
import pika
from dotenv import load_dotenv

from crypto_verify import verify_signature

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
PAYMENT_ACCEPTED_ROUTINGKEY=os.getenv("PAYMENT_ACCEPTED_ROUTINGKEY")
TICKET_GENERATED_ROUTINGKEY=os.getenv("TICKET_GENERATED_ROUTINGKEY")

if not all([RABBITMQ_USER, RABBITMQ_PASS, RABBITMQ_HOST, RABBITMQ_PORT, LOGS_ROUTINGKEY, PAYMENT_ACCEPTED_ROUTINGKEY, TICKET_GENERATED_ROUTINGKEY]):
    raise EnvironmentError("One or more required environment variables are missing.")

##############################################################
#                           CALLBACKS
##############################################################

def payment_accepted_callback(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))

    ch.basic_publish(
        exchange="direct", 
        routing_key=LOGS_ROUTINGKEY, 
        body=f"Payment Accepted Received".encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "ticket"})
    )

    signature = base64.b64decode(data["signature"])
    transaction = data["transaction"]
    transaction_str = json.dumps(transaction, sort_keys=True)

    if not verify_signature(value=transaction_str, sig=signature):
        ch.basic_publish(
            exchange="direct", 
            routing_key=LOGS_ROUTINGKEY, 
            body=f"ERROR: Payment accepted - signature invalid! transaction_id: {transaction["id"]} for reservation_id {transaction["reservation_id"]}".encode("utf-8"), 
            properties=pika.BasicProperties(headers={"sender": "ticket"})
        )
        return
    
    ch.basic_publish(
        exchange="direct", 
        routing_key=LOGS_ROUTINGKEY, 
        body=f"Payment validated - generating tickets! transaction_id: {transaction["id"]} for reservation_id {transaction["reservation_id"]}".encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "ticket"})
    )

    tickets = [{"id": i, "uuid": str(uuid.uuid4())} for i in range(transaction["tickets_num"])]

    return_dict = {
        "tickets": tickets,
        "reservation_id": transaction["reservation_id"]
    }

    ch.basic_publish(
        exchange="direct", 
        routing_key=TICKET_GENERATED_ROUTINGKEY, 
        body=json.dumps(return_dict).encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "ticket"})
    )


##############################################################
#          QUEUES DECLARATION and RABBITMQ SETUP
##############################################################
print("Starting ticket service")

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
channel.exchange_declare(exchange="direct", exchange_type="direct")

# Payment Accepted Queue ->  consumer
queue_name = "payment_accepted_ticket"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange="direct", queue=queue_name, routing_key=PAYMENT_ACCEPTED_ROUTINGKEY)
channel.basic_consume(queue=queue_name, on_message_callback=payment_accepted_callback, auto_ack=True)

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
        print("Stopping ticket service.")
    finally:
        if connection and not connection.is_closed:
            connection.close()

if __name__ == "__main__":
    
    start_rabbitmq_consumer()

##############################################################
