// import React, { useState, useRef, useEffect } from "react";
// import { useNavigate } from "react-router-dom";
// import { Send, Mouse as Museum } from "lucide-react";
// import "../../App.css";

// function Chatbot() {
//     const [messages, setMessages] = useState([
//         { text: "Welcome to Museum Ticket Booking! How can I help?", isBot: true }
//     ]);
//     const [input, setInput] = useState("");
//     const navigate = useNavigate();
//     const messagesEndRef = useRef(null);

//     const scrollToBottom = () => {
//         messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//     };

//     useEffect(() => scrollToBottom(), [messages]);

//     const handleSend = async () => {
//         if (!input.trim()) return;
        
//         const userMessage = input;
//         setInput("");
//         setMessages(prev => [...prev, { text: userMessage, isBot: false }]);

//         try {
//             const response = await fetch("http://localhost:8000/query", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({ request: userMessage })
//             });

//             const data = await response.json();
            
//             setMessages(prev => [...prev, { 
//                 text: data.answer, 
//                 isBot: true 
//             }]);

//             if (data.no_of_tickets > 0 && data.booked_museum_id) {
//                 navigate(`/payment?museum=${data.booked_museum_id}&tickets=${data.no_of_tickets}`);
//             }
//         } catch (error) {
//             setMessages(prev => [...prev, { 
//                 text: "Connection error. Please try again.", 
//                 isBot: true 
//             }]);
//         }
//     };

//     return (
//         <div className="chat-container">
//             <header className="chat-header">
//                 <Museum size={24} />
//                 <h1>Museum Ticket Booking</h1>
//             </header>

//             <main className="chat-messages">
//                 {messages.map((message, index) => (
//                     <div key={index} className={`message-container ${message.isBot ? "align-left" : "align-right"}`}>
//                         <div className={`message-bubble ${message.isBot ? "bot-message" : "user-message"}`}>
//                             {message.text}
//                         </div>
//                     </div>
//                 ))}
//                 <div ref={messagesEndRef} />
//             </main>

//             <footer className="chat-footer">
//                 <input
//                     type="text"
//                     value={input}
//                     onChange={(e) => setInput(e.target.value)}
//                     onKeyDown={(e) => e.key === "Enter" && handleSend()}
//                     placeholder="Type your message..."
//                     className="input-box"
//                 />
//                 <button onClick={handleSend} className="send-button">
//                     <Send size={20} />
//                 </button>
//             </footer>
//         </div>
//     );
// }

// export default Chatbot;
////////
import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Send } from "lucide-react";
import axios from "axios";
import "../../App.css";

// A separate component for individual chat messages.
const ChatMessage = ({ message }) => (
  <div className={message.isBot ? "box-align-left" : "box-align-right"}>
    <div className={`message-bubble ${message.isBot ? "bot-message" : "user-message"}`}>
      {message.text}
    </div>
  </div>
);

function Chatbot() {
  const [messages, setMessages] = useState([
    { text: "Welcome to Museum Ticket Booking! How can I help?", isBot: true }
  ]);
  const [input, setInput] = useState("");
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);

  // Automatically scroll to the bottom whenever messages update.
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput("");
    setMessages(prev => [...prev, { text: userMessage, isBot: false }]);

    try {
      const response = await axios.post("http://localhost:8000/query", { request: userMessage });
      const botResponse = { text: response.data.answer, isBot: true };
      setMessages(prev => [...prev, botResponse]);

      // Redirect if there are tickets to book.
      if (response.data.no_of_tickets > 0 && response.data.booked_museum_id) {
        navigate(`/payment_new?museum_id=${response.data.booked_museum_id}&tickets=${response.data.no_of_tickets}`);
      }
    } catch (error) {
      setMessages(prev => [
        ...prev,
        { text: "Sorry, I'm having trouble connecting. Please try again later.", isBot: true }
      ]);
    }
  };

  return (
    <div className="chat-container">
      <main className="chat-messages">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </main>
      <footer className="chat-footer">
        <input
          type="text"
          className="input-box"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button className="send-button" onClick={handleSend}>
          <Send size={20} />
        </button>
      </footer>
    </div>
  );
}

export default Chatbot;
