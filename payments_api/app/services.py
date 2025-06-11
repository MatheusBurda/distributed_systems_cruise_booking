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

    def create_payment_link(self, amount: float, currency: str, customer_email: str) -> PaymentLink:
        payment_link_id = str(uuid.uuid4())
        created_at = datetime.now(UTC)
        expires_at = created_at + timedelta(hours=24)  # Payment links expire after 24 hours
        
        payment_link = PaymentLink(
            id=payment_link_id,
            amount=amount,
            currency=currency,
            customer_email=customer_email,
            created_at=created_at,
            expires_at=expires_at
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

        current_year = datetime.now(UTC).year
        current_month = datetime.now(UTC).month
        
        if (card_info.expiry_year < current_year or 
            (card_info.expiry_year == current_year and 
             card_info.expiry_month < current_month)):
            raise ValueError("Card has expired")

        if not card_info.number.isdigit() or len(card_info.number) != 4:
            raise ValueError("Invalid card number format")

        payment_id = str(uuid.uuid4())
        payment = Payment(
            id=payment_id,
            amount=payment_link.amount,
            currency=payment_link.currency,
            card_last4=card_info.number,
            customer_email=payment_link.customer_email,
            status=PaymentStatus.PENDING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        
        # Process the payment
        is_successful = random.random() < Config.PAYMENT_SUCCESS_RATE
        payment.status = PaymentStatus.AUTHORIZED if is_successful else PaymentStatus.DECLINED
        payment.updated_at = datetime.now(UTC)
        payment.transaction_id = str(uuid.uuid4()) if is_successful else None
        
        # Mark payment link as used
        payment_link.is_used = True
        
        # Store the payment
        self.payments[payment_id] = payment
        
        # Send webhook notification
        self._send_webhook_notification(payment)
        
        return payment

    def get_payment(self, payment_id: str) -> Payment:
        if payment_id not in self.payments:
            raise ValueError("Payment not found")
        return self.payments[payment_id]

    def _send_webhook_notification(self, payment: Payment):
        """Send webhook notification to the payment service"""
        webhook_data = {
            "payment_id": payment.id,
            "status": payment.status.value,
            "amount": payment.amount,
            "currency": payment.currency,
            "card_last4": payment.card_last4,
            "customer_email": payment.customer_email,
            "transaction_id": payment.transaction_id,
            "timestamp": payment.updated_at.isoformat()
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