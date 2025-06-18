import { FC } from "react";
import { useNavigate } from "react-router-dom";
import { Booking } from "../../../../types";

interface BookingItemProps {
  booking: Booking;
}

const BookingItem: FC<BookingItemProps> = ({ booking }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };
  const navigate = useNavigate();

  const formatDateTime = (dateTimeString: string) => {
    return new Date(dateTimeString).toLocaleString();
  };

  const handleCheckDetails = () => {
    navigate(`/bookings/${booking.id}`);
  };

  return (
    <div className={`booking-item ${booking.status.toLowerCase()}`}>
      <div className="booking-header">
        <h4>Booking #{booking.id}</h4>
        <div className="status-badges">
          <span className={`status-badge ${booking.status.toLowerCase()}`}>
            {booking.status}
          </span>
          <span
            className={`status-badge ${booking.payment_status.toLowerCase()}`}
          >
            {booking.payment_status}
          </span>
        </div>
      </div>

      <div className="reservation-details">
        <div className="detail-row">
          <span className="label">Customer Name:</span>
          <span>{booking.customer_name}</span>
        </div>

        <div className="detail-row">
          <span className="label">Customer Email:</span>
          <span>{booking.customer_email}</span>
        </div>

        <div className="detail-row">
          <span className="label">Origin:</span>
          <span>{booking.origin}</span>
        </div>

        <div className="detail-row">
          <span className="label">Itinerary ID:</span>
          <span>{booking.destination_id}</span>
        </div>

        <div className="detail-row">
          <span className="label">Boarding Date:</span>
          <span>{formatDate(booking.boarding_date)}</span>
        </div>

        <div className="detail-row">
          <span className="label">Cabins:</span>
          <span>{booking.number_of_cabins}</span>
        </div>

        <div className="detail-row">
          <span className="label">Passengers:</span>
          <span>{booking.number_of_passengers}</span>
        </div>

        {/* <div className="detail-row">
          <span className="label">Total Cost:</span>
          <span>${booking.total_cost}</span>
        </div> */}

        {/* <div className="detail-row">
          <span className="label">Payment ID:</span>
          <span>{booking.payment_id}</span>
        </div> */}

        <div className="detail-row">
          <span className="label">Created At:</span>
          <span>{formatDateTime(booking.created_at)}</span>
        </div>
      </div>

      <div className="payment-section">
        <button className="check-details-button" onClick={handleCheckDetails}>
          Check Details
        </button>
      </div>
    </div>
  );
};

export default BookingItem;
