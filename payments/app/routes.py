import base64
from flask import Blueprint, jsonify, request
import json
from app.core.rabbitmq import RabbitMQManager
from app.services.payment_manager import PaymentManager
from app.models.payment import PaymentStatus
from app.core.crypto_sign import signature

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/webhook", methods=["POST"])
def update_payment():
    data = request.json
    
    if not data or "payment_link_external_id" not in data or "status" not in data:
        return jsonify({"error": "Missing payment_link_external_id or status"}), 400
    
    payment_id = data["payment_link_external_id"]
    payment_status = PaymentStatus(data["status"])
    
    payment_manager = PaymentManager()
    payment = payment_manager.get_payment(payment_id)
    
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
        
    payment_manager.update_payment_status(payment.id, payment_status)
    
    rabbitmq_manager = RabbitMQManager()
    transaction_data = {
        "id": payment.id,
        "booking_id": payment.booking_id,
        "status": str(payment_status.value),
        "card_last4": data.get("card_last4", ""),
        "amount": data.get("amount", ""),
        "currency": data.get("currency", ""),
        "transaction_id": data.get("transaction_id", ""),
        "number_of_passengers": payment.number_of_passengers,
        "number_of_cabins": payment.number_of_cabins
    }
    
    transaction_str = json.dumps(transaction_data, sort_keys=True)
    transaction_signature = base64.b64encode(signature(transaction_str)).decode("utf-8")

    message_payload = {
            "transaction": transaction_data,
            "signature": transaction_signature,
    }
    
    print(payment)
    print(transaction_data)

    if payment_status == PaymentStatus.AUTHORIZED:
        rabbitmq_manager.publish_payment_approved(json.dumps(message_payload))
    elif payment_status == PaymentStatus.DECLINED:
        rabbitmq_manager.publish_payment_rejected(json.dumps(message_payload))
    
    return jsonify({
        "status": "success",
        "message": f"Payment {payment_status}",
        "payment": payment.to_dict()
    }), 200

@payments_bp.route("/payment-link", methods=["GET"])
def get_payment_link():
    data = request.json

    required_fields = [
        "booking_id",
        "amount",
        "customer_email",
        "customer_name",
        "number_of_passengers",
        "number_of_cabins"
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
            customer_name=data["customer_name"],
            number_of_passengers=data["number_of_passengers"],
            number_of_cabins=data["number_of_cabins"]
        )
        
        return jsonify({
            "status": "success",
            "message": "Payment link created successfully",
            "payment": payment.to_dict()
        }), 201
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), e.__dict__.get("code", 500)
    