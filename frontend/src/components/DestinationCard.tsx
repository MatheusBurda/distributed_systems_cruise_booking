import { FC } from "react";
import { Destination } from "../types";

interface DestinationCardProps {
  destination: Destination;
  onSelect: () => void;
}

const DestinationCard: FC<DestinationCardProps> = ({
  destination,
  onSelect,
}) => {
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
      </div>

      <div className="places-visited">
        <h4>Places Visited:</h4>
        <p>{destination.places_visited.join(" → ")}</p>
      </div>

      <div className="departure-dates">
        <h4>Departure Dates:</h4>
        <ul>
          {destination.departure_dates.map((date) => (
            <li key={date}>{formatDate(date)}</li>
          ))}
        </ul>
      </div>

      <button className="book-button" onClick={onSelect}>
        Book This Cruise
      </button>
    </div>
  );
};

export default DestinationCard;
