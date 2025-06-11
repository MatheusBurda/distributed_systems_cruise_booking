from enum import Enum

class BookingStatus(Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    BOOKED = "BOOKED"
    COMPLETED = "COMPLETED"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    REJECTED = "REJECTED" 