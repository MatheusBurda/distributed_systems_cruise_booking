from pydantic import BaseModel, Field
from datetime import datetime, UTC
from typing import Optional
from enum import Enum

class PaymentStatus(Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    DECLINED = "DECLINED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class Payment(BaseModel):
    id: str
    booking_id: str
    amount: float
    customer_email: str
    customer_name: str
    status: PaymentStatus = PaymentStatus.PENDING
    payment_link: Optional[str] = None
    payment_link_id: Optional[str] = None
    payment_expires_at: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    number_of_passengers: int
    number_of_cabins: int

    def update_status(self, new_status: str) -> None:
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "amount": self.amount,
            "customer_email": self.customer_email,
            "customer_name": self.customer_name,
            "status": str(self.status.value),
            "payment_link": self.payment_link,
            "payment_link_id": self.payment_link_id,
            "payment_expires_at": self.payment_expires_at,
            "number_of_passengers": self.number_of_passengers,
            "number_of_cabins": self.number_of_cabins,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        } 