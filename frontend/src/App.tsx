import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import DestinationListPage from "./pages/DestinationList";
import BookingListPage from "./pages/BookingList";
import BookingFormPage from "./pages/BookingForm";
import PromotionFormPage from "./pages/PromotionForm";
import BookingDetails from "./pages/BookingDetails";
import Navbar from "./components/Navbar";
import PaymentPage from "./pages/Payment";
import "./App.css";

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname;

  const getActiveSection = () => {
    if (currentPath === "/") return "destinations";
    if (currentPath === "/bookings") return "reservations";
    if (currentPath === "/bookings/new") return "booking";
    if (currentPath === "/promotions") return "promotions";
    if (currentPath.startsWith("/bookings/")) return "booking-details";
    if (currentPath === "/payment") return "payment";
    return "destinations";
  };

  const handleSectionChange = (section: string) => {
    switch (section) {
      case "destinations":
        navigate("/");
        break;
      case "reservations":
        navigate("/bookings");
        break;
      case "booking":
        navigate("/bookings/new");
        break;
      case "promotions":
        navigate("/promotions");
        break;
      case "payment":
        navigate("/payment");
        break;
      default:
        navigate("/");
    }
  };

  return (
    <div className="app-container">
      <Navbar
        activeSection={getActiveSection()}
        setActiveSection={handleSectionChange}
      />
      <main className="content">
        <Routes>
          <Route path="/" element={<DestinationListPage />} />
          <Route path="/bookings" element={<BookingListPage />} />
          <Route path="/bookings/new" element={<BookingFormPage />} />
          <Route path="/bookings/:id" element={<BookingDetails />} />
          <Route path="/promotions" element={<PromotionFormPage />} />
          <Route path="/payment" element={<PaymentPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
