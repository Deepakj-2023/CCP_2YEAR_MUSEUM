import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

function Payment() {
    const [details, setDetails] = useState(null);
    const [error, setError] = useState(null);
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const museumId = params.get("museum");
        const tickets = params.get("tickets");

        console.log("Received Params:", { museumId, tickets }); // Debugging

        if (!museumId || !tickets) {
            setError("Missing museum ID or ticket count.");
            return;
        }

        const fetchDetails = async () => {
            try {
                console.log(`Fetching details from API: http://localhost:8000/pay_details?museum_id=${museumId}&no_of_tickets=${tickets}`);
                
                const response = await fetch(
                    `http://localhost:8000/pay_details?museum_id=${museumId}&no_of_tickets=${tickets}`
                );

                if (!response.ok) {
                    throw new Error(`API error: ${response.statusText}`);
                }

                const data = await response.json();
                setDetails(data);
            } catch (err) {
                console.error("Error fetching payment details:", err);
                setError("Failed to load payment details.");
            }
        };

        fetchDetails();
    }, [location]);

    return (
        <div className="payment-container">
            {error ? (
                <p className="error">{error}</p>
            ) : details ? (
                <>
                    <h2>Payment for {details.museum_name}</h2>
                    <div className="payment-details">
                        <p>Tickets: {details.tickets}</p>
                        <p>Price per ticket: ${details.price.toFixed(2)}</p>
                        <p>Total: ${details.total.toFixed(2)}</p>
                        <button onClick={() => navigate("/confirmation")}>
                            Confirm Payment
                        </button>
                    </div>
                </>
            ) : (
                <p>Loading payment details...</p>
            )}
        </div>
    );
}

export default Payment;
