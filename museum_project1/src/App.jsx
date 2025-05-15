
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./Pages/Chatbot/Navbar";
import MuseumShowcase from "./Pages/Chatbot/MuseumShowcase";
import Chatbot from "./Pages/Chatbot/Chatbot";
import PaymentNew from "./Pages/Chatbot/PaymentNew";
import SuccessPage from "./Pages/Chatbot/SuccessPage";
import FailedPage from "./Pages/Chatbot/FailedPage";

function App() {
    return (
        <Router>
            <Navbar />
            <Routes>
                <Route path="/" element={<MuseumShowcase />} />
                <Route path="/chatbot" element={<Chatbot />} />
                <Route path="/payment_new" element={<PaymentNew />} />
                <Route path="/success" element={<SuccessPage />} />
                <Route path="/failed" element={<FailedPage />} />
            </Routes>
        </Router>
    );
}

export default App;