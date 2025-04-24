import { useState, useEffect, FC } from "react";
import DestinationCard from "./DestinationCard";
import DestinationFilter from "./DestinationFilter";
import { Destination, FilterParams } from "../types";

interface DestinationListProps {
  onSelectDestination: (destination: Destination) => void;
}

const DestinationList: FC<DestinationListProps> = ({ onSelectDestination }) => {
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterParams>({
    origin: "",
    destination: "",
    date: "",
  });

  useEffect(() => {
    const fetchDestinations = async () => {
      try {
        const queryParams = new URLSearchParams();
        if (filters.origin) queryParams.append("origin", filters.origin);
        if (filters.destination)
          queryParams.append("destination", filters.destination);
        if (filters.date) queryParams.append("date", filters.date);

        const url = `${import.meta.env.VITE_API_URL}/destinations${
          queryParams.toString() ? `?${queryParams.toString()}` : ""
        }`;

        const response = await fetch(url);
        if (!response.ok) {
          throw new Error("Failed to fetch destinations");
        }
        const data = await response.json();
        setDestinations(data.destinations);
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

  if (loading) return <div className="loading">Loading destinations...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="destinations-container">
      <h2>Available Cruises</h2>
      <DestinationFilter onFilterChange={handleFilterChange} />

      {destinations.length === 0 ? (
        <p className="no-results">
          No destinations found matching your criteria.
        </p>
      ) : (
        <div className="destination-grid">
          {destinations.map((destination) => (
            <DestinationCard
              key={destination.id}
              destination={destination}
              onSelect={() => onSelectDestination(destination)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default DestinationList;
