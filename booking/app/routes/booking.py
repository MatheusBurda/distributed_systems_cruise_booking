from flask import Blueprint

bookings_bp = Blueprint("bookings", __name__)

@bookings_bp.route("/bookings", methods=["GET"])
def get_bookings():
    pass


@bookings_bp.route("/bookings", methods=["POST"])
def create_booking():
    pass


@bookings_bp.route("/bookings/<booking_id>", methods=["DELETE"])
def cancel_booking(booking_id):
    pass