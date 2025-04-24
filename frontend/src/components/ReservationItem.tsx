import { FC } from "react";
import { Reservation } from "../types";

interface ReservationItemProps {
  reservation: Reservation;
}

const ReservationItem: FC<ReservationItemProps> = ({ reservation }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const formatDateTime = (dateTimeString: string) => {
    return new Date(dateTimeString).toLocaleString();
  };

  return (
    <div className={`reservation-item ${reservation.status.toLowerCase()}`}>
      <div className="reservation-header">
        <h4>Reservation #{reservation.id}</h4>
        <span className={`status-badge ${reservation.status.toLowerCase()}`}>
          {reservation.status}
        </span>
      </div>

      <div className="reservation-details">
        <div className="detail-row">
          <span className="label">Origin:</span>
          <span>{reservation.origin}</span>
        </div>

        <div className="detail-row">
          <span className="label">Destination ID:</span>
          <span>{reservation.destination_id}</span>
        </div>

        <div className="detail-row">
          <span className="label">Boarding Date:</span>
          <span>{formatDate(reservation.boarding_date)}</span>
        </div>

        <div className="detail-row">
          <span className="label">Cabins:</span>
          <span>{reservation.number_of_cabins}</span>
        </div>

        <div className="detail-row">
          <span className="label">Passengers:</span>
          <span>{reservation.number_of_passengers}</span>
        </div>

        <div className="detail-row">
          <span className="label">Total Cost:</span>
          <span>${reservation.total_cost}</span>
        </div>

        <div className="detail-row">
          <span className="label">Created At:</span>
          <span>{formatDateTime(reservation.created_at)}</span>
        </div>
      </div>

      {reservation.tickets && (
        <div className="tickets-section">
          <h5>Tickets</h5>
          <ul className="ticket-list">
            {reservation.tickets.map((ticket) => (
              <li key={ticket.uuid} className="ticket">
                <span className="ticket-id">Ticket #{ticket.id}</span>
                <span className="ticket-uuid">{ticket.uuid}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ReservationItem;
