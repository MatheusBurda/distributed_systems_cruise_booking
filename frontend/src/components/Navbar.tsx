import { FC } from "react";

interface NavbarProps {
  activeSection: string;
  setActiveSection: (section: string) => void;
}

const Navbar: FC<NavbarProps> = ({ activeSection, setActiveSection }) => {
  const navItems = [
    { id: "destinations", label: "Destinations" },
    { id: "reservations", label: "Reservations" },
    { id: "booking", label: "Book a Cruise" },
    { id: "promotions", label: "Create Promotion" },
  ];

  return (
    <nav className="navbar">
      <h1 className="brand">Cruise Bookings</h1>
      <ul className="nav-items">
        {navItems.map((item) => (
          <li
            key={item.id}
            className={activeSection === item.id ? "active" : ""}
          >
            <button onClick={() => setActiveSection(item.id)}>
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Navbar;
