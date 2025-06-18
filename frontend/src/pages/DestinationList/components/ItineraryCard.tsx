import { FC } from "react";
import { Itinerary } from "../../../types";

interface ItineraryCardProps {
  destination: Itinerary;
  onSelect: () => void;
}

const ItineraryCard: FC<ItineraryCardProps> = ({ destination, onSelect }) => {
  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <div className="destination-card">
      <div className="card-header">
        <h3>
          {destination.origin} to {destination.destination}
        </h3>
        <span className="ship-name">{destination.ship_name}</span>
      </div>

      <div className="card-details">
        <div className="detail-item">
          <span className="label">Nights:</span>
          <span>{destination.number_of_nights}</span>
        </div>

        <div className="detail-item">
          <span className="label">Cabin Cost:</span>
          <span>${destination.cabin_cost}</span>
        </div>

        <div className="detail-item">
          <span className="label">Cabin Capacity:</span>
          <span>{destination.cabin_capacity} people</span>
        </div>

        <div className="detail-item">
          <span className="label">Available Cabins:</span>
          <span>{destination.available_cabins}</span>
        </div>

        <div className="detail-item">
          <span className="label">Continent:</span>
          <span>{destination.trip_continent}</span>
        </div>

        <div className="detail-item">
          <span className="label">Return Port:</span>
          <span>{destination.return_port}</span>
        </div>
      </div>

      <div className="places-visited">
        <h4>Places Visited:</h4>
        <p>{destination.places_visited.join(" → ")}</p>
      </div>

      <div className="departure-dates">
        <h4>Departure Date:</h4>
        <p>{formatDate(destination.date)}</p>
      </div>

      <button
        className="book-button"
        onClick={onSelect}
        disabled={destination.available_cabins === 0}
      >
        {destination.available_cabins === 0
          ? "No Cabins Available"
          : "Book This Cruise"}
      </button>
    </div>
  );
};

export default ItineraryCard;
