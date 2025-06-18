import uuid
import random
from datetime import datetime, timedelta, UTC
import requests
from .models import Payment, PaymentRequest, PaymentStatus, PaymentLink, CreditCardInfo
from .config import Config

class PaymentService:
    def __init__(self):
        self.payments = {}
        self.payment_links = {}

    def create_payment_link(self, amount: float, currency: str, customer_email: str, external_id: str) -> PaymentLink:
        payment_link_id = str(uuid.uuid4())
        created_at = datetime.now(UTC)
        expires_at = created_at + timedelta(hours=24)  # Payment links expire after 24 hours
        
        payment_link = PaymentLink(
            id=payment_link_id,
            amount=amount,
            currency=currency,
            customer_email=customer_email,
            created_at=created_at,
            expires_at=expires_at,
            external_id=external_id
        )
        
        self.payment_links[payment_link_id] = payment_link
        return payment_link

    def process_payment_with_link(self, payment_link_id: str, card_info: CreditCardInfo) -> Payment:
        if payment_link_id not in self.payment_links:
            raise ValueError("Payment link not found")
            
        payment_link = self.payment_links[payment_link_id]
        
        if payment_link.is_used:
            raise ValueError("Payment link has already been used")
            
        if datetime.now(UTC) > payment_link.expires_at:
            raise ValueError("Payment link has expired")

        current_year = datetime.now(UTC).year % 100
        current_month = datetime.now(UTC).month
        
        if (card_info.expiry_year < current_year or 
            (card_info.expiry_year == current_year and 
             card_info.expiry_month < current_month)):
            raise ValueError("Card has expired")

        if len(card_info.number) != 16:
            raise ValueError("Invalid card number format")
        
        if len(card_info.cvv) != 3:
            raise ValueError("Invalid CVV format")

        payment_id = str(uuid.uuid4())
        payment = Payment(
            id=payment_id,
            amount=payment_link.amount,
            currency=payment_link.currency,
            card_last4=card_info.number[-4:],
            customer_email=payment_link.customer_email,
            status=PaymentStatus.PENDING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        
        is_successful = self.check_card_with_bank(card_info)
        payment.status = PaymentStatus.AUTHORIZED if is_successful else PaymentStatus.DECLINED
        payment.updated_at = datetime.now(UTC)
        payment.transaction_id = str(uuid.uuid4()) if is_successful else None
        
        payment_link.is_used = True
        
        self.payments[payment_id] = payment
        
        self._send_webhook_notification(payment, payment_link)
        
        return payment
    
    def check_card_with_bank(self, card_info: CreditCardInfo) -> bool:
        if card_info.number == "1111111111111111" or card_info.cvv == "777":
            return False
        return True

    def get_payment(self, payment_id: str) -> Payment:
        if payment_id not in self.payments:
            raise ValueError("Payment not found")
        return self.payments[payment_id]

    def _send_webhook_notification(self, payment: Payment, payment_link: PaymentLink):
        webhook_data = {
            "payment_id": payment.id,
            "status": payment.status.value,
            "amount": payment.amount,
            "currency": payment.currency,
            "card_last4": payment.card_last4,
            "customer_email": payment.customer_email,
            "transaction_id": payment.transaction_id,
            "timestamp": payment.updated_at.isoformat(),
            "payment_link_id": payment_link.id,
            "payment_link_external_id": payment_link.external_id
        }

        try:
            response = requests.post(
                Config.PAYMENT_WEBHOOK_URL,
                json=webhook_data,
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to send webhook notification: {str(e)}")

payment_service = PaymentService() 