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
            body=f"ERROR: Payment accepted - signature invalid! transaction_id: {transaction["id"]} for booking_id {transaction["booking_id"]}".encode("utf-8"), 
            properties=pika.BasicProperties(headers={"sender": "ticket"})
        )
        return
    
    ch.basic_publish(
        exchange="direct", 
        routing_key=LOGS_ROUTING_KEY, 
        body=f"Payment validated - generating tickets! transaction_id: {transaction["id"]} for booking_id {transaction["booking_id"]}".encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "ticket"})
    )

    tickets = []
    num_passengers = transaction["number_of_passengers"]
    num_cabins = transaction.get("number_of_cabins", 1)
    
    passengers_per_cabin = [num_passengers // num_cabins + (1 if i < num_passengers % num_cabins else 0) 
                          for i in range(num_cabins)]
    
    passenger_index = 0
    for cabin_num, cabin_passengers in enumerate(passengers_per_cabin, 1):
        for _ in range(cabin_passengers):
            ticket = Ticket(
                id=passenger_index,
                uuid=uuid.uuid4(),
                booking_id=transaction["booking_id"],
                cabin_number=str(cabin_num),
            )
            tickets.append(ticket)
            passenger_index += 1

    ticket_response = TicketBookingResponse(
        tickets=tickets,
        booking_id=transaction["booking_id"]
    )

    ch.basic_publish(
        exchange="direct", 
        routing_key=TICKET_GENERATED_ROUTING_KEY, 
        body=ticket_response.model_dump_json().encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "ticket"})
    )

    print(f"Ticket generated published for booking_id {transaction['booking_id']} on {TICKET_GENERATED_ROUTING_KEY}")


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
