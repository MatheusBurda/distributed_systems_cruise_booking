from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from datetime import datetime, UTC

class Ticket(BaseModel):
    id: int
    uuid: UUID
    booking_id: str
    cabin_number: str
    departure_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class TicketBookingResponse(BaseModel):
    tickets: List[Ticket]
    booking_id: str
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC)) 