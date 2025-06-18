import { useState, useEffect, FC } from "react";
import { useNavigate } from "react-router-dom";
import ItineraryCard from "./components/ItineraryCard";
import ItineraryFilter from "./components/ItineraryFilter";
import { Itinerary, FilterParams } from "../../types";
import "./styles.css";

const ItineraryListPage: FC = () => {
  const navigate = useNavigate();
  const [destinations, setDestinations] = useState<Itinerary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterParams>({
    origin: "",
    destination: "",
    date: "",
    min_cabins: 0,
    places_visited: "",
    continent: "",
  });

  useEffect(() => {
    const fetchDestinations = async () => {
      try {
        const queryParams = new URLSearchParams();
        if (filters.origin) queryParams.append("origin", filters.origin);
        if (filters.destination)
          queryParams.append("destination", filters.destination);
        if (filters.date) queryParams.append("date", filters.date);
        if (filters.min_cabins)
          queryParams.append("min_cabins", filters.min_cabins.toString());
        if (filters.places_visited)
          queryParams.append("places_visited", filters.places_visited);
        if (filters.continent)
          queryParams.append("continent", filters.continent);

        const url = `${import.meta.env.VITE_API_URL}/itineraries${
          queryParams.toString() ? `?${queryParams.toString()}` : ""
        }`;

        const response = await fetch(url);
        if (!response.ok) {
          throw new Error("Failed to fetch itineraries");
        }
        const data = await response.json();
        setDestinations(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchDestinations();
  }, [filters]);

  const handleFilterChange = (newFilters: FilterParams) => {
    setFilters(newFilters);
  };

  const handleDestinationSelect = (destination: Itinerary) => {
    navigate("/bookings/new", { state: { destination } });
  };

  if (loading) return <div className="loading">Loading destinations...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="destinations-container">
      <h2>Available Cruises</h2>
      <ItineraryFilter onFilterChange={handleFilterChange} />

      {destinations.length === 0 ? (
        <p className="no-results">
          No destinations found matching your criteria.
        </p>
      ) : (
        <div className="destination-grid">
          {destinations.map((destination) => (
            <ItineraryCard
              key={destination.id}
              destination={destination}
              onSelect={() => handleDestinationSelect(destination)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ItineraryListPage;
