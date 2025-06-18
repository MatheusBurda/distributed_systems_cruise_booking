import { useState, useEffect, FC } from "react";
import BookingItem from "./components/BookingItem";
import { Booking } from "../../types";
import "./styles.css";

const BookingListPage: FC = () => {
  const [reservations, setReservations] = useState<Booking[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReservations = async () => {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/bookings`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch reservations");
        }
        const data = await response.json();
        setReservations(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchReservations();
  }, []);

  if (loading) return <div className="loading">Loading bookings...</div>;
  if (error)
    return (
      <div className="error">
        <span style={{ color: "red" }}>Error: {error}</span>
        <button onClick={() => window.location.reload()}>Try again</button>
      </div>
    );

  return (
    <div className="reservations-container">
      <h2>Your Bookings</h2>

      <div className="reservation-section">
        {reservations.length === 0 ? (
          <p className="no-results">No bookings found.</p>
        ) : (
          <div className="reservation-list">
            {reservations.map((booking) => (
              <BookingItem key={booking.id} booking={booking} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BookingListPage;
