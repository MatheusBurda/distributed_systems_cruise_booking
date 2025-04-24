export interface Destination {
  cabin_capacity: number;
  cabin_cost: number;
  departure_dates: string[];
  destination: string;
  id: number;
  number_of_nights: number;
  origin: string;
  places_visited: string[];
  return_port: string;
  ship_name: string;
  trip_continent: string;
}

export interface Ticket {
  id: number;
  uuid: string;
}

export interface Reservation {
  boarding_date: string;
  created_at: string;
  destination_id: number;
  id: string;
  number_of_cabins: number;
  number_of_passengers: number;
  origin: string;
  status: "PAID" | "REJECTED";
  total_cost: number;
  tickets?: Ticket[];
}

export interface BookingFormData {
  number_of_passengers: number;
  boarding_date: string;
  destination_id: number;
  number_of_cabins: number;
  origin: string;
}

export interface PromotionFormData {
  destination_id: number;
  new_cost: number;
  boarding_date: string;
}

export interface FilterParams {
  origin: string;
  destination: string;
  date: string;
}
