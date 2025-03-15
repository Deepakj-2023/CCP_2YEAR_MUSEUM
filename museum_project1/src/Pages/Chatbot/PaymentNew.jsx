// import React, { useState, useEffect } from "react";
// import { useLocation, useNavigate } from "react-router-dom";
// import axios from "axios";

// const PaymentNew = () => {
//   const location = useLocation();
//   const navigate = useNavigate();
//   const [paymentDetails, setPaymentDetails] = useState(null);
//   const [formData, setFormData] = useState({
//     email: "",
//     transactionId: ""
//   });
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState("");

//   useEffect(() => {
//     let isMounted = true;
//     let cancel;

//     const params = new URLSearchParams(location.search);
//     const museumId = params.get("museum_id");
//     const tickets = params.get("tickets");

//     if (!museumId || !tickets) {
//       setError("Invalid booking parameters");
//       setLoading(false);
//       return;
//     }

//     const fetchPaymentDetails = async () => {
//       try {
//         const response = await axios.get("http://localhost:8000/pay_details", {
//           params: {
//             museum_id: parseInt(museumId),
//             no_of_tickets: parseInt(tickets)
//           },
//           cancelToken: new axios.CancelToken(c => (cancel = c))
//         });

//         if (isMounted) {
//           setPaymentDetails(response.data);
//           setError("");
//         }
//       } catch (err) {
//         if (axios.isCancel(err)) return;
//         setError("Failed to load payment details. Please try again.");
//       } finally {
//         if (isMounted) setLoading(false);
//       }
//     };

//     fetchPaymentDetails();

//     return () => {
//       isMounted = false;
//       if (cancel) cancel();
//     };
//   }, [location.search]);

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       await axios.post("http://localhost:8000/confirm_booking", {
//         museum_id: paymentDetails.museum_id,
//         tickets: paymentDetails.tickets,
//         user_upi: formData.transactionId,  // Change `upi_id` to `user_upi`
//         email: formData.email  // Change `user_email` to `email`
//       });
//       navigate("/confirmation");
//     } catch (error) {
//       setError("Booking confirmation failed. Please check your details.");
//     }
//   };

//   if (loading) return <div className="loading">Loading payment details...</div>;
//   if (error) return <div className="error">{error}</div>;

//   return (
//     <div className="payment-container">
//       <h2>Payment for {paymentDetails.museum_name}</h2>
//       <div className="payment-instructions">
//         <p>Send ₹{paymentDetails.total_price} to:</p>
//         <div className="upi-details">
//           <h3>{paymentDetails.upi_id}</h3>
//           <p className="note">(Use any UPI app to complete payment)</p>
//         </div>
//       </div>

//       <form onSubmit={handleSubmit} className="payment-form">
//         <input
//           type="email"
//           placeholder="Enter your email"
//           value={formData.email}
//           onChange={(e) => setFormData({ ...formData, email: e.target.value })}
//           required
//         />
//         <input
//           type="text"
//           placeholder="Enter UPI Transaction ID"
//           value={formData.transactionId}
//           onChange={(e) => setFormData({ ...formData, transactionId: e.target.value })}
//           required
//         />
//         <button type="submit" className="confirm-button">
//           Confirm Payment
//         </button>
//       </form>
//     </div>
//   );
// };

// export default PaymentNew;


/////  next ui desing code 
import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import "./paymentNew.css"; // Import the CSS file

const PaymentNew = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [paymentDetails, setPaymentDetails] = useState(null);
  const [formData, setFormData] = useState({
    email: "",
    transactionId: "",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isMounted = true;
    let cancel;

    const params = new URLSearchParams(location.search);
    const museumId = params.get("museum_id");
    const tickets = params.get("tickets");

    if (!museumId || !tickets) {
      setError("Invalid booking parameters");
      setLoading(false);
      return;
    }

    const fetchPaymentDetails = async () => {
      try {
        const response = await axios.get("http://localhost:8000/pay_details", {
          params: {
            museum_id: parseInt(museumId),
            no_of_tickets: parseInt(tickets),
          },
          cancelToken: new axios.CancelToken((c) => (cancel = c)),
        });

        if (isMounted) {
          setPaymentDetails(response.data);
          setError("");
        }
      } catch (err) {
        if (axios.isCancel(err)) return;
        setError("Failed to load payment details. Please try again.");
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchPaymentDetails();

    return () => {
      isMounted = false;
      if (cancel) cancel();
    };
  }, [location.search]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/confirm_booking", {
        museum_id: paymentDetails.museum_id,
        tickets: paymentDetails.tickets,
        user_upi: formData.transactionId,
        email: formData.email,
      });

      // Redirect to success page with booking details
      navigate("/success", {
        state: {
          museum_name: paymentDetails.museum_name,
          tickets: paymentDetails.tickets,
          user_upi: formData.transactionId,
          total_price: paymentDetails.total_price,
        },
      });
    } catch (error) {
      // Redirect to failed page with error message
      navigate("/failed", {
        state: {
          error_message: error.response?.data?.detail || "Payment failed due to an unknown error.",
        },
      });
    }
  };

  if (loading) return <div className="loading">Loading payment details...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="payment-container">
      <div className="payment-box">
        <h2>Payment for {paymentDetails.museum_name}</h2>
        <div className="payment-instructions">
          <p>Total Amount: ₹{paymentDetails.total_price}</p>
          <p>Admin UPI ID: {paymentDetails.upi_id}</p>
        </div>

        <form onSubmit={handleSubmit} className="payment-form">
          <div className="form-group">
            <label htmlFor="email">EMAIL</label>
            <input
              type="email"
              id="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="transactionId">UPI ID</label>
            <input
              type="text"
              id="transactionId"
              placeholder="Enter your UPI ID"
              value={formData.transactionId}
              onChange={(e) => setFormData({ ...formData, transactionId: e.target.value })}
              required
            />
          </div>
          <button type="submit" className="confirm-button">
            Payment
          </button>
        </form>
      </div>
    </div>
  );
};

export default PaymentNew;