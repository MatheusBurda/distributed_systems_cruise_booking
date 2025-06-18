import { useState, FC, ChangeEvent, FormEvent } from "react";
import { FilterParams } from "../../../types";

interface ItineraryFilterProps {
  onFilterChange: (filters: FilterParams) => void;
}

const ItineraryFilter: FC<ItineraryFilterProps> = ({ onFilterChange }) => {
  const [filters, setFilters] = useState<FilterParams>({
    origin: "",
    destination: "",
    date: "",
    min_cabins: 0,
    places_visited: "",
    continent: "",
  });

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    const updatedFilters = {
      ...filters,
      [name]: name === "min_cabins" ? Number(value) : value,
    };
    setFilters(updatedFilters);
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onFilterChange(filters);
  };

  const handleReset = () => {
    const resetFilters: FilterParams = {
      origin: "",
      destination: "",
      date: "",
      min_cabins: 0,
      places_visited: "",
      continent: "",
    };
    setFilters(resetFilters);
    onFilterChange(resetFilters);
  };

  return (
    <div className="filter-container">
      <h3>Filter Cruises</h3>
      <form onSubmit={handleSubmit} className="filter-form">
        <div className="form-group">
          <label htmlFor="origin">Origin</label>
          <input
            type="text"
            id="origin"
            name="origin"
            value={filters.origin}
            onChange={handleChange}
            placeholder="E.g., Santos"
          />
        </div>

        <div className="form-group">
          <label htmlFor="destination">Destination</label>
          <input
            type="text"
            id="destination"
            name="destination"
            value={filters.destination}
            onChange={handleChange}
            placeholder="E.g., Rio de Janeiro"
          />
        </div>

        <div className="form-group">
          <label htmlFor="date">Departure Date</label>
          <input
            type="date"
            id="date"
            name="date"
            value={filters.date}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="min_cabins">Minimum Available Cabins</label>
          <input
            type="number"
            id="min_cabins"
            name="min_cabins"
            min="0"
            value={filters.min_cabins}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="places_visited">Places Visited</label>
          <input
            type="text"
            id="places_visited"
            name="places_visited"
            value={filters.places_visited}
            onChange={handleChange}
            placeholder="E.g., Rio de Janeiro, Salvador"
          />
        </div>

        <div className="form-group">
          <label htmlFor="continent">Continent</label>
          <input
            type="text"
            id="continent"
            name="continent"
            value={filters.continent}
            onChange={handleChange}
            placeholder="E.g., South America"
          />
        </div>

        <div className="filter-actions">
          <button type="submit" className="btn-filter">
            Apply Filters
          </button>
          <button type="button" className="btn-reset" onClick={handleReset}>
            Reset
          </button>
        </div>
      </form>
    </div>
  );
};

export default ItineraryFilter;
