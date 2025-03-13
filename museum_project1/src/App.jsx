import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./Pages/Chatbot/Navbar";  
import MuseumShowcase from "./Pages/Chatbot/MuseumShowcase";  // Corrected Path
import Chatbot from "./Pages/Chatbot/Chatbot";

function App() {
  return (
    <Router>
      <Navbar />  
      <Routes>
        <Route path="/" element={<MuseumShowcase />} />
        <Route path="/chatbot" element={<Chatbot />} />
      </Routes>
    </Router>
  );
}

export default App;
