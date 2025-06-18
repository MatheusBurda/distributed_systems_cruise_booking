import { useState, FC, FormEvent } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./styles.css";

interface PaymentFormData {
  number: string;
  expiry_month: string;
  expiry_year: string;
  cvv: string;
  holder_name: string;
}

const PaymentPage: FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { paymentLink, bookingId, amount } = location.state || {};

  const [formData, setFormData] = useState<PaymentFormData>({
    number: "",
    expiry_month: "",
    expiry_year: "",
    cvv: "",
    holder_name: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const currentDate = new Date();
      const currentMonth = currentDate.getMonth() + 1;
      const currentYear = currentDate.getFullYear() % 100;

      const expiryMonth = parseInt(formData.expiry_month);
      const expiryYear = parseInt(formData.expiry_year);

      if (
        expiryYear < currentYear ||
        expiryMonth < 1 ||
        expiryMonth > 12 ||
        (expiryYear === currentYear && expiryMonth < currentMonth)
      ) {
        throw new Error("Card expiry date must be in the future");
      }
      const response = await fetch(paymentLink, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Payment failed. Please try again.");
      }

      navigate(`/bookings/${bookingId}`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  if (!paymentLink) {
    return (
      <div className="payment-container">
        <div className="error-message">Invalid payment link</div>
      </div>
    );
  }

  return (
    <div className="payment-container">
      <div className="payment-header">
        <button className="back-button" onClick={() => navigate(-1)}>
          ← Back
        </button>
        <h2>Payment Details</h2>
      </div>

      <div className="payment-card">
        <div className="payment-summary">
          <h3>Payment Summary</h3>
          <div className="amount">${amount}</div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="payment-form">
          <div className="form-group">
            <label htmlFor="holder_name">Cardholder Name</label>
            <input
              type="text"
              id="holder_name"
              name="holder_name"
              value={formData.holder_name}
              onChange={handleChange}
              placeholder="John Doe"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="number">Card Number</label>
            <input
              type="text"
              id="number"
              name="number"
              value={formData.number
                .replace(/\s/g, "")
                .replace(/(\d{4})/g, "$1 ")
                .trim()}
              onChange={handleChange}
              placeholder="1234 5678 9012 3456"
              maxLength={19}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="expiry_month">Expiry Month</label>
              <input
                type="text"
                id="expiry_month"
                name="expiry_month"
                value={formData.expiry_month}
                onChange={handleChange}
                placeholder="MM"
                maxLength={2}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="expiry_year">Expiry Year</label>
              <input
                type="text"
                id="expiry_year"
                name="expiry_year"
                value={formData.expiry_year}
                onChange={handleChange}
                placeholder="YY"
                maxLength={2}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="cvv">CVV</label>
              <input
                type="text"
                id="cvv"
                name="cvv"
                value={formData.cvv}
                onChange={handleChange}
                placeholder="123"
                maxLength={3}
                required
              />
            </div>
          </div>

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? "Processing..." : "Pay Now"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PaymentPage;
