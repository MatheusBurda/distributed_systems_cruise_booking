import { useState, FC, ChangeEvent, FormEvent } from "react";
import { FilterParams } from "../types";

interface DestinationFilterProps {
  onFilterChange: (filters: FilterParams) => void;
}

const DestinationFilter: FC<DestinationFilterProps> = ({ onFilterChange }) => {
  const [filters, setFilters] = useState<FilterParams>({
    origin: "",
    destination: "",
    date: "",
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const updatedFilters = { ...filters, [name]: value };
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

export default DestinationFilter;
