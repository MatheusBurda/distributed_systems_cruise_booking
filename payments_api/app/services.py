import uuid
import random
from datetime import datetime, UTC
import requests
from .models import Payment, PaymentRequest, PaymentStatus
from .config import Config

class PaymentService:
    def __init__(self):
        self.payments = {}

    def create_payment(self, payment_request: PaymentRequest) -> Payment:
        current_year = datetime.now(UTC).year
        current_month = datetime.now(UTC).month
        
        if (payment_request.card_info.expiry_year < current_year or 
            (payment_request.card_info.expiry_year == current_year and 
             payment_request.card_info.expiry_month < current_month)):
            raise ValueError("Card has expired")

        if not payment_request.card_info.number.isdigit() or len(payment_request.card_info.number) != 4:
            raise ValueError("Invalid card number format")

        payment_id = str(uuid.uuid4())
        payment = Payment(
            id=payment_id,
            amount=payment_request.amount,
            currency=payment_request.currency,
            card_last4=payment_request.card_info.number,
            customer_email=payment_request.customer_email,
            status=PaymentStatus.PENDING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        self.payments[payment_id] = payment
        return payment

    def process_payment(self, payment_id: str) -> Payment:
        if payment_id not in self.payments:
            raise ValueError("Payment not found")

        payment = self.payments[payment_id]
        
        is_successful = random.random() < Config.PAYMENT_SUCCESS_RATE
        
        payment.status = PaymentStatus.AUTHORIZED if is_successful else PaymentStatus.DECLINED
        payment.updated_at = datetime.now(UTC)
        payment.transaction_id = str(uuid.uuid4()) if is_successful else None

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