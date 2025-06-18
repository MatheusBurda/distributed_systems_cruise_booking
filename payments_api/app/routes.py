from flask import Blueprint, request, jsonify, current_app
from .services import payment_service
from .models import CreditCardInfo
from .config import Config

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payment-link', methods=['POST'])
def create_payment_link():
    try:
        data = request.get_json()
        
        required_fields = ['amount', 'currency', 'customer_email', 'payment_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        payment_link = payment_service.create_payment_link(
            amount=float(data['amount']),
            currency=data['currency'],
            customer_email=data['customer_email'],
            external_id=data['payment_id']
        )
        
        payment_url = f"http://localhost:{Config.PAYMENT_API_PORT}/payment/{payment_link.id}"
        
        return jsonify({
            'payment_link_id': payment_link.id,
            'payment_url': payment_url,
            'expires_at': payment_link.expires_at.isoformat(),
            'amount': payment_link.amount,
            'currency': payment_link.currency,
            'customer_email': payment_link.customer_email
        }), 201

    except Exception as e:
        current_app.logger.error(f"Error creating payment link: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/payment/<payment_link_id>', methods=['POST'])
def process_payment_with_link(payment_link_id):
    try:
        data = request.get_json()
        
        required_card_fields = ['number', 'expiry_month', 'expiry_year', 'cvv', 'holder_name']
        for field in required_card_fields:
            if field not in data:
                return jsonify({'error': f'Missing required card field: {field}'}), 400

        payment = payment_service.process_payment_with_link(
            payment_link_id=payment_link_id,
            card_info=CreditCardInfo(
                number=data['number'].replace(" ", ""),
                expiry_month=int(data['expiry_month']),
                expiry_year=int(data['expiry_year']),
                cvv=data['cvv'],
                holder_name=data['holder_name']
            )
        )
        return jsonify(payment.to_dict()), 200

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