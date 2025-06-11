from flask import Blueprint, jsonify, request, current_app
import time
import json
import requests
from uuid import uuid4
from app.core.rabbitmq import RabbitMQManager
from app.services.payment_manager import PaymentManager

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/webhook", methods=["GET"])
def update_payment():
    data = request.json
    
    if not data or "payment_id" not in data or "status" not in data:
        return jsonify({"error": "Missing payment_id or status"}), 400
    
    payment_id = data["payment_id"]
    payment_status = data["status"]
    
    payment_manager = PaymentManager()
    payment = payment_manager.get_payment(payment_id)
    
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
        
    payment_manager.update_payment_status(payment.id, payment_status)
    
    rabbitmq_manager = RabbitMQManager()
    transaction_data = {
        "id": payment.id,
        "reservation_id": payment.booking_id,
        "status": payment_status
    }
    
    message_payload = {
        "transaction": transaction_data,
        "signature": data.get("signature", "")
    }
    
    if payment_status == "approved":
        rabbitmq_manager.publish_payment_approved(json.dumps(message_payload))
    elif payment_status == "rejected":
        rabbitmq_manager.publish_payment_rejected(json.dumps(message_payload))
    
    return jsonify({
        "status": "success",
        "message": f"Payment {payment_status}",
        "payment": payment.to_dict()
    }), 200

@payments_bp.route("/payment-link", methods=["POST"])
def get_payment_link():
    data = request.json

    required_fields = [
        "booking_id",
        "amount",
        "customer_email",
        "customer_name"
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        payment_manager = PaymentManager()
        payment = payment_manager.create_payment(
            booking_id=data["booking_id"],
            amount=data["amount"],
            customer_email=data["customer_email"],
            customer_name=data["customer_name"]
        )
        
        return jsonify({
            "status": "success",
            "message": "Payment link created successfully",
            "payment": payment.to_dict()
        }), 201
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), e.__dict__.get("code", 500)
    