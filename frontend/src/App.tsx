import { useState } from "react";
import DestinationList from "./components/DestinationList";
import ReservationList from "./components/ReservationList";
import BookingForm from "./components/BookingForm";
import PromotionForm from "./components/PromotionForm";
import Navbar from "./components/Navbar";
import { Destination } from "./types";
import "./App.css";

function App() {
  const [activeSection, setActiveSection] = useState<string>("destinations");
  const [selectedDestination, setSelectedDestination] =
    useState<Destination | null>(null);

  const handleDestinationSelect = (destination: Destination) => {
    setSelectedDestination(destination);
    setActiveSection("booking");
  };

  const renderContent = () => {
    switch (activeSection) {
      case "destinations":
        return (
          <DestinationList onSelectDestination={handleDestinationSelect} />
        );
      case "reservations":
        return <ReservationList />;
      case "booking":
        return <BookingForm selectedDestination={selectedDestination} />;
      case "promotions":
        return <PromotionForm />;
      default:
        return (
          <DestinationList onSelectDestination={handleDestinationSelect} />
        );
    }
  };

  return (
    <div className="app-container">
      <Navbar
        activeSection={activeSection}
        setActiveSection={setActiveSection}
      />
      <main className="content">{renderContent()}</main>
    </div>
  );
}

export default App;
