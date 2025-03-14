const nodemailer = require("nodemailer");

// Create a transporter object using Gmail
const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
        user: "deepakjgenai@gmail.com", // Your email
        pass: "1914Deepak", // Your App Password
    },
});

// Define email options
const mailOptions = {
    from: "deepakjgenai@gmail.com", // Sender address
    to: "deepakcolab2024@gmail.com", // Recipient address
    subject: "Booking Confirmation", // Subject line
    text: `Booking Confirmed!

    Museum: Bharathiar Museum
    Tickets: 3
    Total Paid: ₹15.00
    Admin UPI ID: admin@bank
    Your UPI ID: user1@bank

    Thank you for your booking!`, // Plain text body
};

// Send the email
transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
        console.log("Error sending email:", error);
    } else {
        console.log("Email sent:", info.response);
    }
});