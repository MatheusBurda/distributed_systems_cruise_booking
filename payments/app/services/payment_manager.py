import requests
from typing import Dict, Optional
from uuid import uuid4
from flask import current_app

from app.models.payment import Payment

class PaymentManager:
    _instance = None
    _initialized = False
    payments: Dict[str, Payment] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PaymentManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not PaymentManager._initialized:
            PaymentManager._initialized = True

    def create_payment(self, booking_id: str, amount: float, customer_email: str, customer_name: str, number_of_passengers: int, number_of_cabins: int) -> Payment:
        payment = Payment(
            id=f"PAY-{uuid4().hex[:8].upper()}",
            booking_id=booking_id,
            amount=amount,
            customer_email=customer_email,
            customer_name=customer_name,
            number_of_passengers=number_of_passengers,
            number_of_cabins=number_of_cabins
        )
        
        try:
            response = requests.post(
                f'http://payments_api:{current_app.config["PAYMENT_API_PORT"]}/payment-link',
                json={
                    "amount": amount,
                    "currency": "USD",
                    "customer_email": customer_email,
                    "customer_name": customer_name,
                    "payment_id": payment.id
                }
            )
            
            if response.status_code != 201:
                raise Exception({"error": f"Failed to create payment link: {response.json()}", "code": response.status_code})
                
            payment_data = response.json()
            payment.payment_link = payment_data.get("payment_url", "")
            payment.payment_link_id = payment_data.get("payment_link_id", "")
            payment.payment_expires_at = payment_data.get("expires_at", "")
            
        except requests.RequestException as e:
            raise Exception({"error": f"Payment API error: {str(e)}", "code": 500})
        
        self.payments[payment.id] = payment
        return payment

    def get_payment(self, payment_id: str) -> Optional[Payment]:
        return self.payments.get(payment_id)

    def update_payment_status(self, payment_id: str, status: str) -> bool:
        payment = self.payments.get(payment_id)
        if not payment:
            return False
            
        payment.update_status(status)
        return True 