// import React from "react";
// import { useLocation } from "react-router-dom";

// const SuccessPage = () => {
//     const location = useLocation();
//     const { museum_name, tickets, user_upi } = location.state || {};

//     return (
//         <div style={{ textAlign: "center", padding: "20px" }}>
//             <h1 style={{ color: "green" }}>Payment Successful!</h1>
//             <div style={{ border: "1px solid #ccc", padding: "20px", maxWidth: "400px", margin: "0 auto", borderRadius: "10px" }}>
//                 <p><strong>Museum:</strong> {museum_name}</p>
//                 <p><strong>Tickets:</strong> {tickets}</p>
//                 <p><strong>UPI ID:</strong> {user_upi}</p>
//                 <p><strong>Message:</strong> Payment successfully completed.</p>
//             </div>
//         </div>
//     );
// };

// export default SuccessPage;/

import React from "react";
import { useLocation } from "react-router-dom";
import "./success.css"; // Import the CSS file

const SuccessPage = () => {
  const location = useLocation();
  const { museum_name, tickets, user_upi, total_price } = location.state || {};

  return (
    <div className="success-container">
      <div className="success-box">
        <h1 className="success-title">Payment Successful!</h1>
        <div className="success-details">
          <p><strong>Museum:</strong> {museum_name}</p>
          <p><strong>Tickets:</strong> {tickets}</p>
          <p><strong>Total Paid:</strong> ₹{total_price}</p>
          <p><strong>UPI ID:</strong> {user_upi}</p>
          <p><strong>Message:</strong> Payment successfully completed.</p>
        </div>
      </div>
    </div>
  );
};

export default SuccessPage;