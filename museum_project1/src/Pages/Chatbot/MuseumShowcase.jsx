import React, { useEffect, useState } from "react";
import axios from "axios";
import "./MuseumShowcase.css";

const MuseumShowcase = () => {
  const [museums, setMuseums] = useState([]);
  const [loading, setLoading] = useState(true); // Loading state

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/museums")
      .then(response => {
        console.log("Fetched Museums Data:", response.data); // Debugging log
        if (Array.isArray(response.data) && response.data.length > 0) {
          setMuseums(response.data);
        } else {
          console.warn("No museum data received:", response.data);
        }
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching data:", error);
        setLoading(false);
      });
  }, []);

  // ✅ Correctly wrap JSX inside the return statement
  return (
    <div className="container">
      <h1>Museum Showcase</h1>

      {loading ? (
        <p>Loading museums...</p>
      ) : (
        <>
          {/* Debugging log on UI */}
          {museums.length === 0 ? (
            <p>No museums available.</p>
          ) : (
            <div className="museum-list">
              {museums.map(museum => (
                <div key={museum.museum_id} className="museum-card">
                  <h2>{museum.museum_name}</h2>
                  <p>{museum.description}</p>
                  <p><strong>Location:</strong> {museum.location}</p>
                  <p><strong>Available Time:</strong> {museum.available_time}</p>
                  <p><strong>Price:</strong> ${museum.price}</p>
                  <p><strong>Tickets Available:</strong> {museum.total_tickets}</p>
                  <p><strong>Best Time to Visit:</strong> {museum.recommended_pick_time}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default MuseumShowcase;
