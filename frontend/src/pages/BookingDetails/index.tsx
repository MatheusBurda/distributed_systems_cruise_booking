import { useState, useEffect, FC } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Booking } from "../../types";
import "./styles.css";

const BookingDetails: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBooking = async () => {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/bookings/${id}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch booking details");
        }
        const data = await response.json();
        setBooking(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchBooking();
    }
  }, [id]);

  if (loading) return <div className="loading">Loading booking details...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!booking) return <div className="error">Booking not found</div>;

  return (
    <div className="booking-details-container">
      <div className="booking-details-header">
        <h2>Booking Details</h2>
        <button className="back-button" onClick={() => navigate("/bookings")}>
          ← Back to Reservations
        </button>
      </div>

      <div className="booking-details-card">
        <div className="booking-header">
          <h3>Booking ID: {booking.id}</h3>

          <div className="info-item">
            <span className={`status-badge ${booking.status.toLowerCase()}`}>
              {booking.status}
            </span>
          </div>
        </div>

        <div className="booking-sections">
          <div className="booking-section">
            <h4>Customer Information</h4>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">Name:</span>
                <span className="info-value">{booking.customer_name}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Email:</span>
                <span className="info-value">{booking.customer_email}</span>
              </div>
            </div>
          </div>

          <div className="booking-section">
            <h4>Trip Details</h4>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">Origin:</span>
                <span className="info-value">{booking.origin}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Boarding Date:</span>
                <span className="info-value">
                  {new Date(booking.boarding_date).toLocaleDateString()}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Number of Passengers:</span>
                <span className="info-value">
                  {booking.number_of_passengers}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Number of Cabins:</span>
                <span className="info-value">{booking.number_of_cabins}</span>
              </div>
            </div>
          </div>

          <div className="booking-section">
            <h4>Payment Details</h4>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">Cost per Cabin:</span>
                <span className="info-value">
                  ${(booking.total_cost / booking.number_of_cabins).toFixed(2)}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Total Cost:</span>
                <span className="info-value cost">
                  ${booking.total_cost.toFixed(2)}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Payment Status:</span>
                <span
                  className={`status-badge ${
                    booking.payment?.status?.toLowerCase() || "pending"
                  }`}
                >
                  {booking.payment?.status || "PENDING"}
                </span>
              </div>
              {booking.payment?.id && (
                <div className="info-item">
                  <span className="info-label">Payment ID:</span>
                  <span className="info-value payment-id">
                    {booking.payment?.id}
                  </span>
                </div>
              )}
            </div>
            {booking.status !== "CANCELLED" && (
              <div className="payment-actions">
                <button
                  className="cancel-button"
                  onClick={() => {
                    if (
                      window.confirm(
                        "Are you sure you want to cancel this booking?"
                      )
                    ) {
                      fetch(
                        `${import.meta.env.VITE_API_URL}/bookings/${
                          booking.id
                        }`,
                        {
                          method: "DELETE",
                        }
                      )
                        .then((response) => {
                          if (!response.ok) {
                            throw new Error("Failed to cancel booking");
                          }
                          window.location.reload();
                        })
                        .catch((error) => {
                          alert("Error cancelling booking: " + error.message);
                        });
                    }
                  }}
                >
                  Cancel Booking
                </button>
                {booking.payment?.status !== "PAID" && (
                  <button
                    className="pay-button"
                    onClick={() =>
                      navigate("/payment", {
                        state: {
                          paymentLink: booking.payment_link,
                          bookingId: booking.id,
                          amount: booking.total_cost.toFixed(2),
                        },
                      })
                    }
                  >
                    Pay Now
                  </button>
                )}
              </div>
            )}
          </div>

          {booking.tickets && (
            <div className="booking-section">
              <h4>Tickets</h4>
              <div className="tickets-list">
                {booking.tickets.tickets.map((ticket) => (
                  <div key={ticket.uuid} className="ticket-item">
                    <div className="ticket-header">
                      <span className="ticket-id">Ticket #{ticket.id}</span>
                      <span className="ticket-uuid">{ticket.uuid}</span>
                    </div>
                    <div className="ticket-details">
                      <span className="ticket-cabin">
                        Cabin: {ticket.cabin_number}
                      </span>
                      <span className="ticket-date">
                        Issued at:{" "}
                        {new Date(ticket.issued_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookingDetails;
