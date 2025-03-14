import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Your email credentials
sender_email = "deepakjgenai@gmail.com"
receiver_email = "deepakcolab2024@gmail.com"
password = "zvhd brey bfks cfgl"  # Your app password

# Set up the server
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(sender_email, password)

# Compose the email
subject = "Success"
body = "This is the message body indicating success of the mail."

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

# Send the email
server.sendmail(sender_email, receiver_email, msg.as_string())

# Close the server connection
server.quit()

print("Email sent successfully!")
