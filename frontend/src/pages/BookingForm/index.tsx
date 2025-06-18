import { useState, useEffect, FC, ChangeEvent, FormEvent } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Itinerary, BookingFormData } from "../../types";
import "./styles.css";

const BookingFormPage: FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const selectedDestination = location.state?.destination as Itinerary | null;

  const [formData, setFormData] = useState<BookingFormData>({
    number_of_passengers: selectedDestination?.cabin_capacity || 2,
    boarding_date: "",
    destination_id: selectedDestination?.id || 0,
    number_of_cabins: 1,
    origin: selectedDestination?.origin || "",
    customer_email: "",
    customer_name: "",
  });

  const [destinations, setDestinations] = useState<Itinerary[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [success, setSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedDestination) {
      const fetchDestinations = async () => {
        try {
          const response = await fetch(
            `${import.meta.env.VITE_API_URL}/itineraries`
          );
          if (!response.ok) {
            throw new Error("Failed to fetch destinations");
          }
          const data = await response.json();
          setDestinations(data);
        } catch (err) {
          setError(`Error fetching destinations: ${(err as Error).message}`);
        }
      };

      fetchDestinations();
    } else {
      setFormData({
        ...formData,
        destination_id: selectedDestination.id,
        origin: selectedDestination.origin,
        number_of_passengers: selectedDestination.cabin_capacity,
      });
    }
  }, [selectedDestination]);

  useEffect(() => {
    if (selectedDestination) {
      setFormData({
        number_of_passengers: selectedDestination.cabin_capacity,
        boarding_date: selectedDestination.date || "",
        destination_id: selectedDestination.id,
        number_of_cabins: 1,
        origin: selectedDestination.origin,
        customer_email: "",
        customer_name: "",
      });
    }
  }, [selectedDestination]);

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]:
        name === "destination_id" || name.includes("number_")
          ? Number(value)
          : value,
    });
  };

  const handleDestinationChange = (e: ChangeEvent<HTMLSelectElement>) => {
    const destinationId = Number(e.target.value);
    const selected = destinations.find((d) => d.id === destinationId);

    if (selected) {
      setFormData({
        ...formData,
        destination_id: destinationId,
        origin: selected.origin,
        boarding_date: selected.date || "",
        number_of_passengers: selected.cabin_capacity,
      });
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/bookings`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to create booking");
      }

      const bookingData = await response.json();
      setSuccess(true);
      navigate(`/bookings/${bookingData.id}`);

      setFormData({
        number_of_passengers: 2,
        boarding_date: "",
        destination_id: 0,
        number_of_cabins: 1,
        origin: "",
        customer_email: "",
        customer_name: "",
      });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const currentDestination =
    selectedDestination ||
    destinations.find((d) => d.id === formData.destination_id);

  return (
    <div className="booking-form-container">
      <h2>Book a Cruise</h2>

      {error && <div className="error-message">{error}</div>}
      {success && (
        <div className="success-message">Booking created successfully!</div>
      )}

      <form onSubmit={handleSubmit} className="booking-form">
        {!selectedDestination && (
          <div className="form-group">
            <label htmlFor="destination_id">Select Destination</label>
            <select
              id="destination_id"
              name="destination_id"
              value={formData.destination_id || ""}
              onChange={handleDestinationChange}
              required
            >
              <option value="">-- Select a Destination --</option>
              {destinations.map((destination) => (
                <option key={destination.id} value={destination.id}>
                  {destination.origin} to {destination.destination} (
                  {destination.ship_name})
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="form-group">
          <label htmlFor="boarding_date">Boarding Date</label>
          <input
            type="date"
            id="boarding_date"
            name="boarding_date"
            value={formData.boarding_date}
            onChange={handleChange}
            disabled
          />
        </div>

        <div className="form-group">
          <label htmlFor="number_of_cabins">Number of Cabins</label>
          <input
            type="number"
            id="number_of_cabins"
            name="number_of_cabins"
            min="1"
            value={formData.number_of_cabins}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="number_of_passengers">Number of Passengers</label>
          <input
            type="number"
            id="number_of_passengers"
            name="number_of_passengers"
            min="1"
            max={
              currentDestination
                ? currentDestination.cabin_capacity * formData.number_of_cabins
                : 10
            }
            value={formData.number_of_passengers}
            onChange={handleChange}
            required
          />
          {currentDestination && (
            <small className="form-hint">
              Maximum {currentDestination.cabin_capacity} passengers per cabin.
              Total capacity:{" "}
              {currentDestination.cabin_capacity * formData.number_of_cabins}{" "}
              passengers.
            </small>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="origin">Origin Port</label>
          <input
            type="text"
            id="origin"
            name="origin"
            value={formData.origin}
            onChange={handleChange}
            required
            readOnly={!!selectedDestination}
          />
        </div>

        <div className="form-group">
          <label htmlFor="customer_name">Full Name</label>
          <input
            type="text"
            id="customer_name"
            name="customer_name"
            value={formData.customer_name}
            onChange={handleChange}
            required
            placeholder="Enter your full name"
          />
        </div>

        <div className="form-group">
          <label htmlFor="customer_email">Email</label>
          <input
            type="email"
            id="customer_email"
            name="customer_email"
            value={formData.customer_email}
            onChange={handleChange}
            required
            placeholder="Enter your email"
          />
        </div>

        <button type="submit" className="btn-book" disabled={loading}>
          {loading ? "Creating Booking..." : "Book Now"}
        </button>
      </form>
    </div>
  );
};

export default BookingFormPage;
