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
            "departure_date": self.departure_date.isoformat(),
            "issued_at": self.issued_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ticket':
        return cls(
            id=data["id"],
            uuid=data["uuid"],
            booking_id=data["booking_id"],
            cabin_number=data["cabin_number"],
            departure_date=datetime.fromisoformat(data["departure_date"]),
            issued_at=datetime.fromisoformat(data["issued_at"])
        )

class TicketBookingResponse(BaseModel):
    tickets: List[Ticket]
    booking_id: str
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC)) 

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tickets": [ticket.to_dict() for ticket in self.tickets],
            "booking_id": self.booking_id,
            "issued_at": self.issued_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TicketBookingResponse':
        return cls(
            tickets=[Ticket.from_dict(ticket) for ticket in data["tickets"]],
            booking_id=data["booking_id"],
            issued_at=datetime.fromisoformat(data["issued_at"])
        )