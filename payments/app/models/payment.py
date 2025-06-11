from pydantic import BaseModel, Field
from datetime import datetime, UTC
from typing import Optional

class Payment(BaseModel):
    id: str
    booking_id: str
    amount: float
    customer_email: str
    customer_name: str
    status: str = "pending"
    payment_link: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

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
            "status": self.status,
            "payment_link": self.payment_link,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        } 