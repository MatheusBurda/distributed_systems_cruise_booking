import requests
from flask import Blueprint, current_app, request

itineraries_bp = Blueprint("itineraries", __name__)

@itineraries_bp.route("/itineraries", methods=["GET"])
def get_itineraries():
    filters = {}

    if request.args.get('origin'):
        filters['origin'] = request.args.get('origin')
    if request.args.get('destination'):
        filters['destination'] = request.args.get('destination')
    if request.args.get('places_visited'):
        filters['places_visited'] = request.args.getlist('places_visited')
    if request.args.get('date'):
        filters['date'] = request.args.get('date')
    if request.args.get('min_cabins'):
        filters['min_cabins'] = request.args.get('min_cabins', type=int)
    if request.args.get('continent'):
        filters['continent'] = request.args.get('continent')

    response = requests.get(f'http://itinerary:{current_app.config["ITINERARY_MS_PORT"]}/itineraries', params=filters)
    
    return response.json()