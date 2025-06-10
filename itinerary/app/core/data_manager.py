import json

class DataManager:
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
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not DataManager._initialized:
            try:
                with open("./itinerarios_portugues.json", "r", encoding="utf-8") as file:
                    self.data = json.load(file)
                
                if (not self.data):
                    raise Exception("No data loaded from itinerary file")
                
                DataManager._initialized = True
            except Exception as e:
                print(f"Failed loading itinerary file {e}")

    def get_itinerary_by_id(self, itinerary_id: int) -> dict:
        for itinerary in self.data:
            if itinerary["id"] == itinerary_id:
                return itinerary
        return None

    def get_itineraries(self):
        return self.data

    def _normalize_text(self, text: str) -> str:
        """Remove accents and convert to lowercase for text comparison."""
        import unicodedata
        return unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('ASCII')
    

    def filter_itineraries(self, filters: dict) -> list:
        """
        Filter itineraries based on multiple criteria.
        
        Args:
            filters (dict): Dictionary containing filter criteria:
                - origin (str): Origin city
                - destination (str): Destination
                - places_visited (list): List of places to visit
                - date (str): Departure date
                - min_cabins (int): Minimum available cabins
                - continent (str): Trip continent
        
        Returns:
            list: Filtered list of itineraries
        """
        itineraries = self.data

        filters_itineraries = []

        if filters['origin'] is not None:
            filters_itineraries.append(lambda x: x['origin'] == filters['origin'])

        if filters['destination'] is not None:
            filters_itineraries.append(lambda x: x['destination'] == filters['destination'])

        if filters['places_visited'] is not None:
            filters_itineraries.append(lambda x: set(self._normalize_text(place) for place in filters['places_visited']).issubset(
                set(self._normalize_text(place) for place in x['places_visited'])))

        if filters['date'] is not None:
            filters_itineraries.append(lambda x: x['date'] == filters['date'])

        if filters['min_cabins'] is not None:
            filters_itineraries.append(lambda x: x['available_cabins'] >= filters['min_cabins'])

        if filters['continent'] is not None:
            filters_itineraries.append(lambda x: x['trip_continent'].lower() == filters['continent'].lower())

        filtered_itineraries = [item for item in itineraries if all(f(item) for f in filters_itineraries)]
            
        return filtered_itineraries
    
    def register_booking(self, destination_id, cabins):
        """
        Register a booking by removing the specified number of cabins from the destination.
        
        Args:
            destination_id (int): ID of the destination to book
            cabins (int): Number of cabins to book
        """
        for itinerary in self.data:
            if itinerary['id'] == destination_id:
                itinerary['available_cabins'] -= cabins
                break

    def register_cancellation(self, destination_id, cabins):
        """
        Register a cancellation by adding the specified number of cabins to the destination.
        
        Args:
            destination_id (int): ID of the destination to cancel
            cabins (int): Number of cabins to cancel
        """
        for itinerary in self.data:
            if itinerary['id'] == destination_id:
                itinerary['available_cabins'] += cabins
                break
