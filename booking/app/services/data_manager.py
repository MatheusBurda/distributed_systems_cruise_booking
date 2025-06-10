import json

class ReservationsManager:
    """
    DataManager is a singleton class that manages the data for the itinerary service.
    It loads the data from the itinerary file and provides a method to get the itineraries.
    """
    _instance = None
    _initialized = False

    # Data structure:
    #   {
    #     "id": 99,
    #     "destination": "Mar Adriático",
    #     "origin": "Veneza",
    #     "ship_name": "Costa Deliziosa",
    #     "return_port": "Veneza",
    #     "places_visited": ["Veneza", "Split", "Bari", "Dubrovnik", "Koper"],
    #     "number_of_nights": 7,
    #     "cabin_cost": 4150.0,
    #     "cabin_capacity": 2,
    #     "trip_continent": "Europa",
    #     "date": "2026-09-15",
    #     "available_cabins": 5
    #   }
    data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ReservationsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not ReservationsManager._initialized:
            try:
                with open("./itinerarios_portugues.json", "r", encoding="utf-8") as file:
                    self.data = json.load(file)
                
                if (not self.data):
                    raise Exception("No data loaded from itinerary file")
                
                ReservationsManager._initialized = True
            except Exception as e:
                print(f"Failed loading itinerary file {e}")

    def _normalize_text(self, text: str) -> str:
        """Remove accents and convert to lowercase for text comparison."""
        import unicodedata
        return unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('ASCII')

    
    def create_booking(self, destination_id, cabins):
        """
        Register a booking by removing the specified number of cabins from the destination.
        
        Args:
            destination_id (int): ID of the destination to book
            cabins (int): Number of cabins to book
        """
        for itinerary in self.data:
            if itinerary['id'] == destination_id:
                itinerary['available_cabins'] -= cabins
                return True
        return False

    def cancel_booking(self, destination_id, cabins):
        """
        Register a cancellation by adding the specified number of cabins to the destination.
        
        Args:
            destination_id (int): ID of the destination to cancel
            cabins (int): Number of cabins to cancel
        """
        for itinerary in self.data:
            if itinerary['id'] == destination_id:
                itinerary['available_cabins'] += cabins
                return True
        return False
    
    def register_payment_accepted(self, booking_id, payment):
        pass

    def register_payment_rejected(self, booking_id, payment):
        pass

    def register_ticket_generated(self, booking_id, ticket):
        pass

