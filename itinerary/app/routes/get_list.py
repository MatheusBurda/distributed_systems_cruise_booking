from flask import Blueprint, jsonify, request
from app.core.data_manager import DataManager

itineraries_bp = Blueprint("itineraries", __name__)
data_manager = DataManager()

@itineraries_bp.route("/itineraries", methods=["GET"])
def get_itineraries():
    
    filters = {
        "origin": request.args.get('origin'),
        "destination": request.args.get('destination'),
        "places_visited": request.args.getlist('places_visited'),
        "date": request.args.get('date'),
        "min_cabins": request.args.get('min_cabins', type=int),
        "continent": request.args.get('continent')
    }

    itineraries = data_manager.filter_itineraries(filters)
    
    return jsonify(itineraries)