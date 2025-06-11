from flask import Blueprint, request, jsonify, current_app
from .services import payment_service
from .models import PaymentRequest, CreditCardInfo

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payment', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()
        
        required_fields = ['amount', 'currency', 'card_info', 'customer_email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        card_info = data['card_info']
        required_card_fields = ['number', 'expiry_month', 'expiry_year', 'cvv']
        for field in required_card_fields:
            if field not in card_info:
                return jsonify({'error': f'Missing required card field: {field}'}), 400

        payment_request = PaymentRequest(
            amount=float(data['amount']),
            currency=data['currency'],
            card_info=CreditCardInfo(
                number=card_info['number'],
                expiry_month=int(card_info['expiry_month']),
                expiry_year=int(card_info['expiry_year']),
                cvv=card_info['cvv']
            ),
            customer_email=data['customer_email']
        )

        payment = payment_service.create_payment(payment_request)
        processed_payment = payment_service.process_payment(payment.id)
        
        return jsonify(processed_payment.to_dict()), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error processing payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/payment/<payment_id>', methods=['GET'])
def get_payment(payment_id):
    try:
        payment = payment_service.get_payment(payment_id)
        return jsonify(payment.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 