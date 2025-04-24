import base64
import json
import time
import uuid
from crypto_sign import signature

def accept_payment(reservation_data):
    total_cost = reservation_data["total_cost"]
    reservation_id = reservation_data["id"]
    tickets_num = reservation_data["number_of_passengers"]

    transaction_details = {
        "amount": total_cost,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "id": str(uuid.uuid4()),
        "reservation_id": reservation_id,
        "status": "ACCEPTED",
        "tickets_num": tickets_num
    }

    transaction_str = json.dumps(transaction_details, sort_keys=True)
    transaction_signature = base64.b64encode(signature(transaction_str)).decode("utf-8")

    return {
        "transaction": transaction_details,
        "signature": transaction_signature
    }


def reject_payment(reservation_data):
    total_cost = reservation_data["total_cost"]
    reservation_id = reservation_data["id"]
    tickets_num = reservation_data["number_of_passengers"]

    transaction_details = {
        "amount": total_cost,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "id": str(uuid.uuid4()),
        "reservation_id": reservation_id,
        "status": "REJECTED",
        "tickets_num": tickets_num
    }

    transaction_str = json.dumps(transaction_details, sort_keys=True)
    transaction_signature = base64.b64encode(signature(transaction_str)).decode("utf-8")

    return {
        "transaction": transaction_details,
        "signature": transaction_signature
    }