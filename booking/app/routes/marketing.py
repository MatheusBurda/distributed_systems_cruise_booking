from flask import Blueprint, jsonify, request

from app.services.marketing_manager import MarketingManager

marketing_bp = Blueprint("marketing", __name__)

@marketing_bp.route("/marketing/subscribe", methods=["POST"])
def subscribe():
    user_id = request.json.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    marketing_manager = MarketingManager()
    marketing_manager.subscribe(user_id)

    return jsonify({"message": "Subscribed to marketing notifications"}), 200


@marketing_bp.route("/marketing/unsubscribe", methods=["DELETE"])
def unsubscribe():
    user_id = request.json.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    marketing_manager = MarketingManager()
    marketing_manager.unsubscribe(user_id)

    return jsonify({"message": "Unsubscribed from marketing notifications"}), 200
    