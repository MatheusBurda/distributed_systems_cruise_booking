import { useState, useEffect, ChangeEvent, FormEvent } from "react";
import { Itinerary, PromotionFormData } from "../../types";
import "./styles.css";

function PromotionFormPage() {
  const [formData, setFormData] = useState<PromotionFormData>({
    destination_id: 0,
    boarding_date: "",
    new_cost: 0,
  });

  const [destinations, setDestinations] = useState<Itinerary[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [formLoading, setFormLoading] = useState<boolean>(false);
  const [success, setSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDestinations = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/itineraries`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch destinations");
        }
        const data = await response.json();
        setDestinations(data);
      } catch (err: any) {
        setError(`Error fetching destinations: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchDestinations();
  }, []);

  useEffect(() => {
    if (formData.destination_id) {
      const selected = destinations.find(
        (d) => d.id === Number(formData.destination_id)
      );
      if (selected) {
        setFormData((prev) => ({
          ...prev,
          boarding_date: "",
          new_cost: selected.cabin_cost * 0.8,
        }));
      }
    }
  }, [formData.destination_id, destinations]);

  const handleChange = (
    e: ChangeEvent<HTMLSelectElement | HTMLInputElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === "destination_id"
          ? value === ""
            ? ""
            : Number(value)
          : name === "new_cost"
          ? value === ""
            ? ""
            : parseFloat(value)
          : value,
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL_PROMOTIONS}/promotion`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to create promotion");
      }

      setSuccess(true);
      setFormData({
        destination_id: 0,
        boarding_date: "",
        new_cost: 0,
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setFormLoading(false);
    }
  };

  const currentDestination =
    formData.destination_id !== 0
      ? destinations.find((d) => d.id === Number(formData.destination_id))
      : undefined;

  if (loading)
    return <div className="loading">Loading destination data...</div>;

  return (
    <div className="promotion-form-container">
      <h2>Create Promotion</h2>

      {error && <div className="error-message">{error}</div>}
      {success && (
        <div className="success-message">Promotion created successfully!</div>
      )}

      <form onSubmit={handleSubmit} className="promotion-form">
        <div className="form-group">
          <label htmlFor="destination_id">Select Destination</label>
          <select
            id="destination_id"
            name="destination_id"
            value={formData.destination_id}
            onChange={handleChange}
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

        {currentDestination && (
          <div className="form-group">
            <label htmlFor="boarding_date">Boarding Date</label>
            <select
              id="boarding_date"
              name="boarding_date"
              value={formData.boarding_date}
              onChange={handleChange}
              required
            >
              <option value="">-- Select a Date --</option>
              <option value={currentDestination.date}>
                {currentDestination.date}
              </option>
            </select>
          </div>
        )}

        {currentDestination && (
          <div className="form-group">
            <label htmlFor="new_cost">New Cabin Cost ($)</label>
            <input
              type="number"
              id="new_cost"
              name="new_cost"
              min="0"
              step="0.01"
              value={formData.new_cost}
              onChange={handleChange}
              required
            />
            <small className="form-hint">
              Original cost: ${currentDestination.cabin_cost}.
              {formData.new_cost !== 0 && (
                <span>
                  {" "}
                  Discount:{" "}
                  {(
                    (1 -
                      Number(formData.new_cost) /
                        currentDestination.cabin_cost) *
                    100
                  ).toFixed(0)}
                  %
                </span>
              )}
            </small>
          </div>
        )}

        {currentDestination && (
          <div className="destination-info">
            <h4>Destination Details</h4>
            <p>
              <strong>Ship:</strong> {currentDestination.ship_name}
            </p>
            <p>
              <strong>Number of Nights:</strong>{" "}
              {currentDestination.number_of_nights}
            </p>
            <p>
              <strong>Cabin Capacity:</strong>{" "}
              {currentDestination.cabin_capacity} passengers
            </p>
            <p>
              <strong>Places Visited:</strong>{" "}
              {currentDestination.places_visited.join(", ")}
            </p>
          </div>
        )}

        <button
          type="submit"
          className="btn-create-promotion"
          disabled={
            formLoading || !formData.boarding_date || formData.new_cost === 0
          }
        >
          {formLoading ? "Creating..." : "Create Promotion"}
        </button>
      </form>
    </div>
  );
}

export default PromotionFormPage;
