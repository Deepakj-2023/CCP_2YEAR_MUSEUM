import React from "react";
import { useLocation } from "react-router-dom";

const FailedPage = () => {
    const location = useLocation();
    const { error_message } = location.state || {};

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h1 style={{ color: "red" }}>Payment Failed!</h1>
            <div style={{ border: "1px solid #ccc", padding: "20px", maxWidth: "400px", margin: "0 auto", borderRadius: "10px" }}>
                <p><strong>Reason:</strong> {error_message}</p>
            </div>
        </div>
    );
};

export default FailedPage;