from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel

class PaymentStatus(Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    DECLINED = "declined"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class CreditCardInfo(BaseModel):
    number: str
    expiry_month: int
    expiry_year: int
    cvv: str

class PaymentRequest(BaseModel):
    amount: float
    currency: str
    card_info: CreditCardInfo
    customer_email: str


class Payment(BaseModel):
    id: str
    amount: float
    currency: str
    card_last4: str
    customer_email: str
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    transaction_id: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "currency": self.currency,
            "card_last4": self.card_last4,
            "customer_email": self.customer_email,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "transaction_id": self.transaction_id
        } 