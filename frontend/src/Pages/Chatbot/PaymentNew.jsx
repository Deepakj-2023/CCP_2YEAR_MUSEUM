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
import "./paymentNew.css"; // Your CSS for styling

const PaymentNew = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [paymentDetails, setPaymentDetails] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    email: "",
    contact: "",
  });

  // Fetch payment details from your backend
  useEffect(() => {
    let isMounted = true;
    const params = new URLSearchParams(location.search);
    const museumId = params.get("museum_id");
    const tickets = params.get("tickets");

    if (!museumId || !tickets) {
      setError("Invalid booking parameters");
      setLoading(false);
      return;
    }

    axios
      .get("http://localhost:8000/pay_details", {
        params: {
          museum_id: parseInt(museumId),
          no_of_tickets: parseInt(tickets),
        },
      })
      .then((response) => {
        if (isMounted) {
          setPaymentDetails(response.data);
          setError("");
        }
      })
      .catch((err) => {
        setError("Failed to load payment details. Please try again.");
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [location.search]);

  // Load Razorpay checkout script
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const handlePayment = async () => {
    try {
      // Explicitly convert total_price to a number
      const amountToSend = Number(paymentDetails.total_price);
      console.log("Sending amount:", amountToSend); // Log on the client side

      const orderResponse = await axios.post("http://localhost:8000/create_order", {
        amount: amountToSend, // Ensure this is a number
      });
  
      const order = orderResponse.data.order;
      // Setup Razorpay options
      const options = {
        key: "rzp_test_51rS7QQtpBRH8y", // Replace with your Razorpay public key
        amount: order.amount,
        currency: order.currency,
        name: paymentDetails.museum_name,
        description: "Ticket Payment",
        order_id: order.id,
        prefill: {
          email: formData.email,
          contact: formData.contact,
        },
        handler: async (response) => {
          // When payment is successful, capture the payment or confirm booking
          try {
            console.log(response.razorpay_payment_id);
            console.log(response.razorpay_order_id);
            console.log(paymentDetails.total_price);
            const captureResponse = await axios.post("http://localhost:8000/capture_payment", {
              payment_id: response.razorpay_payment_id,
              amount: paymentDetails.total_price, // in rupees
              sender_upi: formData.contact // or another appropriate value
            });
            // Optionally, you can then call confirm_booking if needed
            // navigate("/success", { state: { ... } });
            navigate("/success", {
              state: {
                museum_name: paymentDetails.museum_name,
                tickets: paymentDetails.tickets,
                user_upi: formData.contact,
                total_price: paymentDetails.total_price,
              },
            });
          } catch (err) {
            navigate("/failed", {
              state: {
                error_message:
                  err.response?.data?.detail || "Payment failed due to an unknown error.",
              },
            });
          }
        },
        theme: {
          color: "#3399cc",
        },
      };

      const rzp = new window.Razorpay(options);
      rzp.open();
    } catch (err) {
      setError("Payment initiation failed. Please try again.");
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

        <form className="payment-form" onSubmit={(e) => { e.preventDefault(); handlePayment(); }}>
          <div className="form-group">
            <label htmlFor="email">EMAIL</label>
            <input
              type="email"
              id="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="contact">CONTACT</label>
            <input
              type="text"
              id="contact"
              placeholder="Enter your contact number"
              value={formData.contact}
              onChange={(e) =>
                setFormData({ ...formData, contact: e.target.value })
              }
              required
            />
          </div>
          <button type="submit" className="confirm-button">
            Pay with Razorpay
          </button>
        </form>
      </div>
    </div>
  );
};

export default PaymentNew;
