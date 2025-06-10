from flask import Blueprint, jsonify, request, current_app
import time
import json
from uuid import uuid4
from app.core.rabbitmq import RabbitMQManager

promotions_bp = Blueprint("promotions", __name__)

@promotions_bp.route("/promotion", methods=["POST"])
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

    rabbitmq_manager = RabbitMQManager()
    rabbitmq_manager.publish_promotion(
        routing_key=current_app.config['LOGS_ROUTING_KEY'], 
        message=f"Creating promotion to destination {data["destination_id"]}", 
        headers={"sender": "promotions"}
    )

    routing_key = str(current_app.config['MARKETING_ROUTING_KEY']) + f".{data["destination_id"]}"

    rabbitmq_manager.publish_promotion(
        routing_key= routing_key,
        message=json.dumps(promotion), 
        headers={"sender": "promotions"}
    )
    
    return jsonify({
        "status": "success",
        "message": "Promotion created successfully",
        "promotion": promotion
    }), 201
