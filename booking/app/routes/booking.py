import json
import requests
from flask import Blueprint, request, jsonify, current_app

from app.services.booking_manager import BookingsManager
from app.core.rabbitmq import RabbitMQManager

bookings_bp = Blueprint("bookings", __name__)

@bookings_bp.route("/bookings", methods=["GET"])
def get_bookings():
    try:
        bookings = BookingsManager().get_all_bookings()
        list_bookings = [booking.to_dict() for booking in bookings]
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), e.__dict__.get("code", 500)
    return jsonify(list_bookings if len(list_bookings) else [])

@bookings_bp.route("/bookings/<booking_id>", methods=["GET"])
def get_booking(booking_id):
    try:
        booking = BookingsManager().get_booking(booking_id)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), e.__dict__.get("code", 500)
    
    return jsonify(booking.to_dict() if booking else {})


@bookings_bp.route("/bookings", methods=["POST"])
def create_booking():
    data = request.json
    try:
        booking = BookingsManager().create_booking(**data)

        rabbitmq_manager = RabbitMQManager()
        rabbitmq_manager.publish_log(f"Booking created: {booking.id}")
        rabbitmq_manager.publish_booking_created(json.dumps({
            "destination_id": booking.destination_id,
            "number_of_cabins": booking.number_of_cabins,
            "customer_email": booking.customer_email,
            "customer_name": booking.customer_name
        }))

        payment_link = None
        try:
            payment_response = requests.get(
                f'http://payments:{current_app.config["PAYMENT_MS_PORT"]}/payment-link',
                json={
                    "booking_id": booking.id,
                    "amount": booking.total_cost,
                    "customer_email": booking.customer_email,
                    "customer_name": booking.customer_name,
                    "number_of_passengers": booking.number_of_passengers,
                    "number_of_cabins": booking.number_of_cabins
                }
            )

            if payment_response.status_code == 201:
                payment_data = payment_response.json()
                payment_link = payment_data.get("payment", {}).get("payment_link")
            else:
                print(f"Failed to get payment link: {payment_response.status_code}")
                
        except requests.RequestException as e:
            print(f"Error calling payments service: {str(e)}")

        booking.payment_link = payment_link
        booking_response = booking.to_dict()
            
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), e.__dict__.get("code", 500)
    
    return jsonify(booking_response)


@bookings_bp.route("/bookings/<booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    try:
        result = BookingsManager().cancel_booking(booking_id)

        rabbitmq_manager = RabbitMQManager()
        rabbitmq_manager.publish_log(f"Booking cancelled: {booking_id}")  
        rabbitmq_manager.publish_booking_cancelled(json.dumps({
            "destination_id": result.destination_id,
            "number_of_cabins": result.number_of_cabins,
            "customer_email": result.customer_email,
            "customer_name": result.customer_name
        }))
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), e.__dict__.get("code", 500)
    
    return jsonify(result.to_dict())