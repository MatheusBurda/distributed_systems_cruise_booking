from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, UTC
from typing import List, Dict, Any

class Ticket(BaseModel):
    id: int
    uuid: UUID
    booking_id: str
    cabin_number: str
    departure_date: datetime
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC)) 

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "uuid": self.uuid,
            "booking_id": self.booking_id,
            "cabin_number": self.cabin_number,
            "departure_date": self.departure_date.isoformat()
        }

class TicketBookingResponse(BaseModel):
    tickets: List[Ticket]
    reservation_id: str
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC)) 

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tickets": [ticket.to_dict() for ticket in self.tickets],
            "reservation_id": self.reservation_id,
            "issued_at": self.issued_at.isoformat()
        }