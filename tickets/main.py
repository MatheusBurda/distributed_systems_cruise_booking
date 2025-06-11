import base64
import os
import json
import uuid
import pika
from datetime import datetime, UTC
from dotenv import load_dotenv
from models import Ticket, TicketBookingResponse

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
LOGS_ROUTING_KEY = os.getenv("LOGS_ROUTING_KEY")
PAYMENT_ACCEPTED_ROUTING_KEY=os.getenv("PAYMENT_ACCEPTED_ROUTING_KEY")
TICKET_GENERATED_ROUTING_KEY=os.getenv("TICKET_GENERATED_ROUTING_KEY")

if not all([RABBITMQ_USER, RABBITMQ_PASS, RABBITMQ_HOST, RABBITMQ_PORT, LOGS_ROUTING_KEY, PAYMENT_ACCEPTED_ROUTING_KEY, TICKET_GENERATED_ROUTING_KEY]):
    raise EnvironmentError("One or more required environment variables are missing.")

##############################################################
#                           CALLBACKS
##############################################################

def payment_accepted_callback(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))

    ch.basic_publish(
        exchange="direct", 
        routing_key=LOGS_ROUTING_KEY, 
        body=f"Payment Accepted Received".encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "ticket"})
    )

    signature = base64.b64decode(data["signature"])
    transaction = data["transaction"]
    transaction_str = json.dumps(transaction, sort_keys=True)

    if not verify_signature(value=transaction_str, sig=signature):
        ch.basic_publish(
            exchange="direct", 
            routing_key=LOGS_ROUTING_KEY, 
            body=f"ERROR: Payment accepted - signature invalid! transaction_id: {transaction["id"]} for reservation_id {transaction["reservation_id"]}".encode("utf-8"), 
            properties=pika.BasicProperties(headers={"sender": "ticket"})
        )
        return
    
    ch.basic_publish(
        exchange="direct", 
        routing_key=LOGS_ROUTING_KEY, 
        body=f"Payment validated - generating tickets! transaction_id: {transaction["id"]} for reservation_id {transaction["reservation_id"]}".encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "ticket"})
    )

    # Create tickets with minimal information
    tickets = []
    for i in range(transaction["tickets_num"]):
        ticket = Ticket(
            id=i,
            uuid=uuid.uuid4(),
            booking_id=transaction["reservation_id"],
            cabin_number=transaction.get("cabin_number", "Unknown"),
            departure_date=datetime.fromisoformat(transaction.get("departure_date", datetime.now(UTC).isoformat()))
        )
        tickets.append(ticket)

    ticket_response = TicketBookingResponse(
        tickets=tickets,
        reservation_id=transaction["reservation_id"]
    )

    ch.basic_publish(
        exchange="direct", 
        routing_key=TICKET_GENERATED_ROUTING_KEY, 
        body=ticket_response.model_dump_json().encode("utf-8"), 
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
channel.queue_bind(exchange="direct", queue=queue_name, routing_key=PAYMENT_ACCEPTED_ROUTING_KEY)
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
