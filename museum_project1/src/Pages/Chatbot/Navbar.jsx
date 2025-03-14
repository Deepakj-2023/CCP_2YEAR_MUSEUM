// import React from "react";
// import { Link } from "react-router-dom";

// const Navbar = () => {
//   return (
//     <nav style={{ display: "flex", gap: "20px", padding: "10px", background: "#222" }}>
//       <Link to="/" style={{ color: "white", textDecoration: "none" }}>Home</Link>
//       <Link to="/chatbot" style={{ color: "white", textDecoration: "none" }}>Chatbot</Link>
//     </nav>
//   );
// };

// export default Navbar;

// Navbar.jsx
import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          Museum Booking
        </Link>
        <div className="nav-menu">
          <Link to="/" className="nav-item">
            Home
          </Link>
          <Link to="/chatbot" className="nav-item">
            Chat Booking
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;