export interface Itinerary {
  available_cabins: number;
  cabin_capacity: number;
  cabin_cost: number;
  date: string;
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
  booking_id: string;
  cabin_number: string;
  departure_date: string;
  issued_at: string;
}

export interface TicketBookingResponse {
  tickets: Ticket[];
  reservation_id: string;
  issued_at: string;
}

export interface Payment {
  id: string;
  booking_id: string;
  amount: number;
  currency: string;
  status: "PENDING" | "PAID" | "REJECTED";
  transaction_id: string;
  created_at: string;
  updated_at: string;
  signature: string;
  card_last4: string;
}

export interface Booking {
  boarding_date: string;
  created_at: string;
  destination_id: number;
  id: string;
  number_of_cabins: number;
  number_of_passengers: number;
  origin: string;
  customer_email: string;
  customer_name: string;
  status:
    | "PAID"
    | "REJECTED"
    | "CREATED"
    | "BOOKED"
    | "CANCELLED"
    | "COMPLETED";
  payment?: Payment;
  total_cost: number;
  payment_link?: string;
  tickets?: TicketBookingResponse;
}

export interface BookingFormData {
  number_of_passengers: number;
  boarding_date: string;
  destination_id: number;
  number_of_cabins: number;
  origin: string;
  customer_email: string;
  customer_name: string;
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
  min_cabins: number;
  places_visited: string;
  continent: string;
}
