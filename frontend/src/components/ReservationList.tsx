import { useState, useEffect, FC } from "react";
import ReservationItem from "./ReservationItem";
import { Reservation } from "../types";

const ReservationList: FC = () => {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReservations = async () => {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/reservations`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch reservations");
        }
        const data = await response.json();
        setReservations(data.reservations);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchReservations();
  }, []);

  if (loading) return <div className="loading">Loading reservations...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  const paidReservations = reservations.filter((res) => res.status === "PAID");
  const rejectedReservations = reservations.filter(
    (res) => res.status === "REJECTED"
  );

  return (
    <div className="reservations-container">
      <h2>Your Reservations</h2>

      <div className="reservation-section">
        <h3>Confirmed Bookings</h3>
        {paidReservations.length === 0 ? (
          <p className="no-results">No confirmed bookings found.</p>
        ) : (
          <div className="reservation-list">
            {paidReservations.map((reservation) => (
              <ReservationItem key={reservation.id} reservation={reservation} />
            ))}
          </div>
        )}
      </div>

      <div className="reservation-section">
        <h3>Failed Bookings</h3>
        {rejectedReservations.length === 0 ? (
          <p className="no-results">No failed bookings found.</p>
        ) : (
          <div className="reservation-list">
            {rejectedReservations.map((reservation) => (
              <ReservationItem key={reservation.id} reservation={reservation} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReservationList;
