from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, UTC
from .base import BookingStatus
from .payment import Payment
from .ticket import TicketBookingResponse

class Booking(BaseModel):
    id: str
    uuid: UUID
    number_of_passengers: int
    origin: str
    destination_id: int
    boarding_date: str
    number_of_cabins: int
    total_cost: float
    customer_email: str
    customer_name: str
    status: BookingStatus = BookingStatus.CREATED
    payment: Optional[Payment] = None
    payment_link: Optional[str] = None
    tickets: Optional[TicketBookingResponse] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    additional_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('id')
    @classmethod
    def validate_id_format(cls, v):
        if not v.startswith('RES-'):
            raise ValueError('Booking ID must start with RES-')
        return v

    @field_validator('number_of_passengers', 'number_of_cabins')
    @classmethod
    def validate_positive_numbers(cls, v):
        if v <= 0:
            raise ValueError('Value must be positive')
        return v

    @field_validator('total_cost')
    @classmethod
    def validate_total_cost(cls, v):
        if v < 0:
            raise ValueError('Total cost cannot be negative')
        return v

    def update_status(self, new_status: BookingStatus) -> None:
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def update_payment(self, new_payment: Payment) -> None:
        self.payment = new_payment
        self.updated_at = datetime.now(UTC)

    def add_tickets(self, new_tickets: TicketBookingResponse) -> None:
        self.tickets.extend(new_tickets)
        self.updated_at = datetime.now(UTC)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "number_of_passengers": self.number_of_passengers,
            "origin": self.origin,
            "destination_id": self.destination_id,
            "boarding_date": self.boarding_date,
            "number_of_cabins": self.number_of_cabins,
            "total_cost": self.total_cost,
            "customer_email": self.customer_email,
            "customer_name": self.customer_name,
            "status": str(self.status.value),
            "payment": self.payment.to_dict() if self.payment else None,
            "payment_link": self.payment_link,
            "tickets": self.tickets.to_dict() if self.tickets else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            **self.additional_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Booking':
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if isinstance(data.get('uuid'), str):
            data['uuid'] = UUID(data['uuid'])
        if isinstance(data.get('status'), str):
            data['status'] = BookingStatus(data['status'])
        if 'payment' in data:
            data['payment'] = Payment(**data['payment'])
        if 'tickets' in data:
            data['tickets'] = TicketBookingResponse(**data['tickets']).tickets
        
        return cls(**data)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        } 