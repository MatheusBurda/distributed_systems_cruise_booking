import base64
import enum
import os
import json
import time
import pika
import threading
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

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
PAYMENT_REJECTED_ROUTINGKEY=os.getenv("PAYMENT_REJECTED_ROUTINGKEY")
PAYMENT_ACCEPTED_ROUTINGKEY=os.getenv("PAYMENT_ACCEPTED_ROUTINGKEY")
TICKET_GENERATED_ROUTINGKEY=os.getenv("TICKET_GENERATED_ROUTINGKEY")
RESERVATION_CREATED_ROUTINGKEY = os.getenv("RESERVATION_CREATED_ROUTINGKEY")

if not all([
    RABBITMQ_USER, 
    RABBITMQ_PASS, 
    RABBITMQ_HOST, 
    RABBITMQ_PORT, 
    RESERVATION_CREATED_ROUTINGKEY, 
    LOGS_ROUTINGKEY, 
    PAYMENT_REJECTED_ROUTINGKEY, 
    PAYMENT_ACCEPTED_ROUTINGKEY, 
    TICKET_GENERATED_ROUTINGKEY
    ]):
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
        properties=pika.BasicProperties(headers={"sender": "reservation"})
    )

    signature = base64.b64decode(data["signature"])
    transaction = data["transaction"]
    transaction_str = json.dumps(transaction, sort_keys=True)

    if not verify_signature(value=transaction_str, sig=signature):
        ch.basic_publish(
            exchange="direct", 
            routing_key=LOGS_ROUTINGKEY, 
            body=f"ERROR: Payment accepted - signature invalid! transaction_id: {transaction["id"]} for reservation_id {transaction["reservation_id"]}".encode("utf-8"), 
            properties=pika.BasicProperties(headers={"sender": "reservation"})
        )
        return

    reservation = [r for r in reservations if r.get("id") == transaction["reservation_id"]][0]

    if reservation:
        reservation["status"] = ReservationStatus.PAID.value

def payment_rejected_callback(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))

    ch.basic_publish(
        exchange="direct", 
        routing_key=LOGS_ROUTINGKEY, 
        body=f"Payment Rejected Received".encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "reservation"})
    )

    signature = base64.b64decode(data["signature"])
    transaction = data["transaction"]
    transaction_str = json.dumps(transaction, sort_keys=True)

    if not verify_signature(value=transaction_str, sig=signature):
        ch.basic_publish(
            exchange="direct", 
            routing_key=LOGS_ROUTINGKEY, 
            body=f"ERROR: Payment rejected signature invalid! transaction_id: {transaction["id"]} for reservation_id {transaction["reservation_id"]}".encode("utf-8"), 
            properties=pika.BasicProperties(headers={"sender": "reservation"})
        )
        return

    reservation = [r for r in reservations if r.get("id") == transaction["reservation_id"]][0]

    if reservation:
        reservation["status"] = ReservationStatus.REJECTED.value


def ticket_generated_callback(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))

    ch.basic_publish(
        exchange="direct", 
        routing_key=LOGS_ROUTINGKEY, 
        body=f"Tickets Created Received".encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "reservation"})
    )

    reservation = [r for r in reservations if r.get("id") == data["reservation_id"]][0]

    if reservation:
        reservation["tickets"] = data["tickets"]

##############################################################
#          QUEUES DECLARATION and RABBITMQ SETUP
##############################################################
print("Starting reservation service")

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
queue_name = "payment_accepted_reservation"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange="direct", queue=queue_name, routing_key=PAYMENT_ACCEPTED_ROUTINGKEY)
channel.basic_consume(queue=queue_name, on_message_callback=payment_accepted_callback, auto_ack=True)

# Payment Rejected Queue ->  consumer
queue_name = "payment_rejected_reservation"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange="direct", queue=queue_name, routing_key=PAYMENT_REJECTED_ROUTINGKEY)
channel.basic_consume(queue=queue_name, on_message_callback=payment_rejected_callback, auto_ack=True)

# Ticket Generated Queue ->  consumer
queue_name = "ticket_created_reservation"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange="direct", queue=queue_name, routing_key=TICKET_GENERATED_ROUTINGKEY)
channel.basic_consume(queue=queue_name, on_message_callback=ticket_generated_callback, auto_ack=True)

print("Finished setup. All queues declared")

##############################################################
#                     RESERVATION API
##############################################################
app = Flask(__name__)
CORS(app, origins="*")

with open("./itinerarios_portugues.json", "r", encoding="utf-8") as file:
    destinations = json.load(file)

reservations = []

class ReservationStatus(enum.Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    REJECTED="REJECTED"
    COMPLETED = "COMPLETED"

flask_connection = None
flask_channel = None

def get_flask_rabbitmq_channel():
    global flask_connection, flask_channel
    
    if flask_connection is None or flask_connection.is_closed:
        flask_connection = create_rabbitmq_connection()
        flask_channel = flask_connection.channel()
        flask_channel.queue_declare(queue="flask_logs_queue", durable=True)
        flask_channel.queue_declare(queue="flask_reservations_queue", durable=True)
        
    return flask_channel

@app.route("/destinations", methods=["GET"])
def list_reservations():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    date = request.args.get("date")
    
    filtered_destinations = destinations
    
    if origin:
        filtered_destinations = [r for r in filtered_destinations if r.get("origin", "").lower() == origin.lower()]
    
    if destination:
        filtered_destinations = [r for r in filtered_destinations if r.get("destination", "").lower() == destination.lower()]
    
    if date:
        filtered_destinations = [r for r in filtered_destinations if r.get("date") == date]
    
    return jsonify({
        "count": len(filtered_destinations),
        "destinations": filtered_destinations
    })

@app.route("/reservations", methods=["GET"])
def get_reservations():
    return jsonify({
        "reservations": reservations
    })

@app.route("/reservation", methods=["POST"])
def create_reservation():
    data = request.json
    
    required_fields = [
        "number_of_passengers", 
        "boarding_date", 
        "destination_id", 
        "number_of_cabins", 
        "origin"
    ]
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400
    
    destination = next((
        d for d in destinations if data["boarding_date"] in d["departure_dates"] 
        and d["origin"].lower() == data["origin"].lower() 
        and d["id"] == int(data["destination_id"])
        ), None )
    if destination is None:
        return jsonify({"error": "No matching destination found"}), 404

    reservation_id = f"RES-{len(reservations) + 1}-{int(time.time())}"
    
    reservation = {
        "id": reservation_id,
        "number_of_passengers": int(data["number_of_passengers"]),
        "origin": data["origin"],
        "destination_id": int(data["destination_id"]),
        "boarding_date": data["boarding_date"],
        "number_of_cabins": int(data["number_of_cabins"]),
        "total_cost": destination["cabin_cost"] * int(data["number_of_cabins"]),
        "status": ReservationStatus.CREATED.value,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        **{k: v for k, v in data.items() if k not in ["id", "status", "created_at"]}
    }
    
    reservations.append(reservation)
    
    channel = get_flask_rabbitmq_channel()
    channel.basic_publish(
        exchange="direct", 
        routing_key=LOGS_ROUTINGKEY, 
        body=f"creating reservation with id {reservation_id}".encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "reservation"})
    )

    channel.basic_publish(
        exchange="direct", 
        routing_key=RESERVATION_CREATED_ROUTINGKEY, 
        body=json.dumps(reservation).encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "reservation"})
    )
    
    return jsonify({
        "status": "success",
        "message": "Reservation created successfully",
        "reservation": reservation
    }), 201


def run_flask_api(host="0.0.0.0", port=5000):
    app.run(host=host, port=port, debug=False)


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
        if flask_connection and not flask_connection.is_closed:
            flask_connection.close()


if __name__ == "__main__":
    api_port = int(os.environ.get("API_PORT", 5000))
    flask_thread = threading.Thread(target=run_flask_api, kwargs={"port": api_port})
    flask_thread.daemon = True
    flask_thread.start()
    
    start_rabbitmq_consumer()

##############################################################
