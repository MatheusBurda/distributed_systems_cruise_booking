import json
from typing import Dict, List, Optional
from uuid import uuid4
from flask import current_app
import requests
from time import sleep

from app.models.itinerary import Itinerary
from app.models.booking import Booking
from app.models.base import BookingStatus, PaymentStatus
from app.models.ticket import TicketBookingResponse

class BookingsManager:
    _instance = None
    _initialized = False

    bookings: Dict[str, Booking] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BookingsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not BookingsManager._initialized:
            try:
                BookingsManager._initialized = True
            except Exception as e:
                print(f"Failed loading itinerary file {e}")

    def get_itinerary(self, itinerary_id: int) -> Optional[Itinerary]:
        response = requests.get(f'http://itinerary:{current_app.config["ITINERARY_MS_PORT"]}/itineraries/{itinerary_id}')

        if response.status_code != 200:
            raise Exception({"error": "Itinerary not found", "code": 404})

        itinerary = Itinerary(**response.json())

        return itinerary

    def create_booking(self, 
                       boarding_date: str,
                       destination_id: int, 
                       number_of_cabins: int, 
                       number_of_passengers: int, 
                       origin: str,
                       customer_email: str,
                       customer_name: str
                    ) -> Optional[Booking]:
        
        itinerary = self.get_itinerary(destination_id)
        
        if itinerary.available_cabins < number_of_cabins:
            raise Exception({"error": "Not enough cabins available", "code": 400})
                
        booking = Booking(
            id=f"RES-{uuid4().hex[:8].upper()}",
            uuid=uuid4(),
            number_of_passengers=number_of_passengers,
            origin=origin,
            destination_id=destination_id,
            boarding_date=boarding_date,
            number_of_cabins=number_of_cabins,
            total_cost=itinerary.cabin_cost * number_of_cabins,
            customer_email=customer_email,
            customer_name=customer_name,
            status=BookingStatus.CREATED,
            payment_status=PaymentStatus.PENDING
        )
        
        self.bookings[booking.id] = booking

        return booking


    def cancel_booking(self, booking_id: str) -> Booking:
        booking = self.bookings.get(booking_id)
        if not booking:
            raise Exception({"error": "Booking not found", "code": 404})
            
        booking.update_status(BookingStatus.CANCELLED)
        # booking.update_payment_status(PaymentStatus.CANCELLED, None)

        updated_booking = self.get_booking(booking_id)

        return updated_booking
    
    def register_payment_accepted(self, booking_id: str, payment_id: str) -> bool:
        booking = self.bookings.get(booking_id)
        if not booking:
            return False
            
        booking.update_payment_status(PaymentStatus.PAID, payment_id)
        booking.update_status(BookingStatus.PAID)

        return True

    def register_payment_rejected(self, booking_id: str, payment_id: str) -> bool:
        booking = self.bookings.get(booking_id)
        if not booking:
            return False
            
        booking.update_payment_status(PaymentStatus.REJECTED, payment_id)
        booking.update_status(BookingStatus.REJECTED)

        return True

    def register_ticket_generated(self, booking_id: str, ticket_response: TicketBookingResponse) -> bool:
        booking = self.bookings.get(booking_id)
        if not booking:
            return False
            
        booking.tickets = ticket_response
        booking.update_status(BookingStatus.BOOKED)

        return True

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        return self.bookings.get(booking_id)

    def get_all_bookings(self) -> List[Booking]:
        return list(self.bookings.values())

