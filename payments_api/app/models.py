from datetime import datetime, UTC
from typing import Optional
from enum import Enum
from dataclasses import dataclass

class PaymentStatus(Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    DECLINED = "DECLINED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

@dataclass
class CreditCardInfo:
    number: str
    expiry_month: int
    expiry_year: int
    cvv: str
    holder_name: str

@dataclass
class PaymentRequest:
    amount: float
    currency: str
    card_info: CreditCardInfo
    customer_email: str

@dataclass
class PaymentLink:
    id: str
    amount: float
    currency: str
    customer_email: str
    created_at: datetime
    expires_at: datetime
    external_id: str
    is_used: bool = False

@dataclass
class Payment:
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