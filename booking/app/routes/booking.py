import json
from flask import Blueprint, request, jsonify
from time import sleep

from app.services.booking_manager import BookingsManager
from app.core.rabbitmq import RabbitMQManager

bookings_bp = Blueprint("bookings", __name__)

@bookings_bp.route("/bookings", methods=["GET"])
def get_bookings():
    try:
        bookings = BookingsManager().get_all_bookings()
        list_bookings = [booking.to_dict() for booking in bookings]
    except Exception as e:
        return jsonify({"error": str(e)}), e.__dict__.get("code", 500)
    return jsonify(list_bookings)


@bookings_bp.route("/bookings", methods=["POST"])
def create_booking():
    data = request.json
    try:
        booking = BookingsManager().create_booking(**data)

        rabbitmq_manager = RabbitMQManager()
        rabbitmq_manager.publish_log(f"Booking created: {booking.id}")
        rabbitmq_manager.publish_booking_created(json.dumps({
            "destination_id": booking.destination_id,
            "number_of_cabins": booking.number_of_cabins
        }))
    except Exception as e:
        return jsonify({"error": str(e)}), e.__dict__.get("code", 500)
    return jsonify(booking.to_dict())


@bookings_bp.route("/bookings/<booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    try:
        result = BookingsManager().cancel_booking(booking_id)

        rabbitmq_manager = RabbitMQManager()
        rabbitmq_manager.publish_log(f"Booking cancelled: {booking_id}")  
        rabbitmq_manager.publish_booking_cancelled(json.dumps({
            "destination_id": result.destination_id,
            "number_of_cabins": result.number_of_cabins
        }))
    except Exception as e:
        return jsonify({"error": str(e)}), e.__dict__.get("code", 500)
    
    return jsonify(result.to_dict())