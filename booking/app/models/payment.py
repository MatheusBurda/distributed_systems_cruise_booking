from typing import Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime, UTC
from .base import PaymentStatus

class Payment(BaseModel):
    id: str
    booking_id: str
    amount: float
    currency: str
    status: PaymentStatus
    transaction_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    signature: str
    card_last4: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        return cls(**data)

