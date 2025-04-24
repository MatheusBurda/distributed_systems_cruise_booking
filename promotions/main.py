import enum
import os
import json
import time
from uuid import uuid4
import pika
import threading
from dotenv import load_dotenv
from flask import Flask, jsonify, request

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
LOGS_ROUTINGKEY = os.getenv("LOGS_ROUTINGKEY")
PROMOTIONS_ROUTINGKEY=os.getenv("PROMOTIONS_ROUTINGKEY")

if not all([
    RABBITMQ_USER, 
    RABBITMQ_PASS, 
    RABBITMQ_HOST, 
    RABBITMQ_PORT, 
    LOGS_ROUTINGKEY, 
    PROMOTIONS_ROUTINGKEY
    ]):
    raise EnvironmentError("One or more required environment variables are missing.")

##############################################################
#          QUEUES DECLARATION and RABBITMQ SETUP
##############################################################
print("Starting promotions service")

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

def get_flask_rabbitmq_channel():
    global connection, channel
    
    if connection is None or connection.is_closed:
        connection = create_rabbitmq_connection()
        channel = connection.channel()
        channel.queue_declare(queue="flask_logs_queue", durable=True)
        channel.queue_declare(queue="flask_promotions_queue", durable=True)
        
    return channel

print("Finished setup. All queues declared")

##############################################################
#                     PROMOTIONS API
##############################################################
app = Flask(__name__)

@app.route("/promotion", methods=["POST"])
def create_promotion():
    print('called /promotion')
    data = request.json
    
    required_fields = [
        "destination_id", 
        "new_cost", 
        "boarding_date"
    ]
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400
    
    promotion = {
        "id": str(uuid4()),
        "destination_id": int(data["destination_id"]),
        "boarding_date": data["boarding_date"],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "new_cost": data["new_cost"]
    }

    channel = get_flask_rabbitmq_channel()
    channel.basic_publish(
        exchange="direct", 
        routing_key=LOGS_ROUTINGKEY, 
        body=f"Creating promotion to destination {data["destination_id"]}".encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "promotions"})
    )

    routing_key = str(PROMOTIONS_ROUTINGKEY) + f".{data["destination_id"]}"

    channel.basic_publish(
        exchange="promotions_topic", 
        routing_key= routing_key,
        body=json.dumps(promotion).encode("utf-8"), 
        properties=pika.BasicProperties(headers={"sender": "promotions"})
    )
    
    return jsonify({
        "status": "success",
        "message": "Promotion created successfully",
        "promotion": promotion
    }), 201


def run_flask_api(host="0.0.0.0", port=5000):
    app.run(host=host, port=port, debug=False)


##############################################################
#                     START SERVICES
##############################################################

if __name__ == "__main__":
    api_port = int(os.environ.get("MARKETING_API_PORT", 5000))
    run_flask_api("0.0.0.0", api_port)

##############################################################
