import logging
import os
import smtplib
import razorpay
from decimal import Decimal
from email.mime.text import MIMEText
from schemas import BookingRequest, PaymentRequest, Response,OrderRequest
import google.generativeai as genai
from database.database import Database
from database.models import MockBank, Museum
from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from io import BytesIO

import qrcode

load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Gemini Configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Email Configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize Razorpay client globally using environment variables
razor_client = razorpay.Client(auth=(os.getenv("Razor_Pay_Key"), os.getenv("Razor_Secret_key")))

print(f"deepak {os.getenv('Razor_Pay_Key')}, and {os.getenv('Razor_Secret_key')}")
@app.get("/museums")
def get_museums(db: Session = Depends(Database.get_db)):
    museums = db.query(Museum).all()  # Fetch using ORM
    return [
        {
            "museum_id": m.museum_id,
            "museum_name": m.museum_name,
            "description": m.description,
            "location": m.location,
            "available_time": m.available_time,
            "price": float(m.price),  # Convert Decimal to float
            "total_tickets": m.total_tickets,
            "recommended_pick_time": m.recommended_pick_time,
        }
        for m in museums
    ]


# Initialize Admin Account
def initialize_admin_account(db: Session):
    admin_upi = "admin@bank"
    admin_account = db.query(MockBank).filter(MockBank.upi_id == admin_upi).first()

    if not admin_account:
        admin_account = MockBank(
            upi_id=admin_upi,
            account_holder_name="Admin",
            phone_number="0000000000",
            balance=Decimal("100000.00"),  # Set a high balance for the admin
            is_admin=True,
        )
        db.add(admin_account)
        db.commit()
        logger.info("Admin account created successfully")
    else:
        logger.info("Admin account already exists")


# Call this function during application startup
@app.on_event("startup")
def on_startup():
    db = next(Database.get_db())
    try:
        initialize_admin_account(db)
    finally:
        db.close()

history = []


def send_confirmation_email(email: str, booking_details: dict):
    # Debug: Print sender and receiver email
    logger.info(f"Sender Email (From .env): {EMAIL_ADDRESS}")
    logger.info(f"Receiver Email (User Provided): {email}")

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logger.warning("Email credentials missing - skipping email send")
        return

    # Debug: Print booking details
    logger.info(f"Booking Details: {booking_details}")

    # Debug: Print email and password (for debugging only - remove in production)
    logger.info(f"Using Email: {EMAIL_ADDRESS}")
    logger.info(
        f"Using Password: {'*' * len(EMAIL_PASSWORD)}"
    )  # Mask password for security

    # Generate QR code data
    qr_data = (
        f"Museum: {booking_details['museum_name']}\n"
        f"Tickets: {booking_details['tickets']}\n"
        f"Admin UPI ID: {booking_details['admin_upi']}\n"
        f"Your UPI ID: {booking_details['user_upi']}"
    )
    logger.info(f"QR Code Data: {qr_data}")

    # Generate QR code in memory
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image to a BytesIO object (in memory)
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)  # Reset the stream position to the beginning

    # Create email content
    email_content = f"""
    <html>
        <body>
            <h1>Booking Confirmed!</h1>
            <p>Museum: {booking_details['museum_name']}</p>
            <p>Tickets: {booking_details['tickets']}</p>
            <p>Total Paid: ₹{booking_details['total_price']:.2f}</p>
            <p>Admin UPI ID: {booking_details['admin_upi']}</p>
            <p>Your UPI ID: {booking_details['user_upi']}</p>
            <p>Thank you for your booking!</p>
            <p>Here is your QR code:</p>
            <img src="cid:qr_code_image">
        </body>
    </html>
    """
    logger.info(f"Email Content: {email_content}")

    # Create the email
    msg = MIMEMultipart()
    msg["Subject"] = "Museum Booking Confirmation"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    # Attach the HTML content
    msg.attach(MIMEText(email_content, "html"))

    # Attach the QR code image from memory
    img_mime = MIMEImage(img_bytes.read(), name="qr_code.png")
    img_mime.add_header("Content-ID", "<qr_code_image>")
    msg.attach(img_mime)

    try:
        # Debug: Print SMTP server details
        logger.info("Connecting to SMTP server...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            logger.info("Logging into SMTP server...")
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            logger.info("Sending email...")
            smtp.send_message(msg)
            logger.info(f"Confirmation email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        # Debug: Print the full error traceback
        import traceback

        logger.error(traceback.format_exc())


# Gemini Functions
def generate_gemini_prompt(user_query: str, db: Session):
    museums = db.query(Museum).all()
    museum_data = "\n".join(
        [
            f"""
    Museum ID: {m.museum_id}
    Name: {m.museum_name}
    Location: {m.location}
    Description: {m.description}
    Price: {m.price}
    Available Tickets: {m.total_tickets}
    Available Time: {m.available_time}
    Recommended Pick Time: {m.recommended_pick_time}
    """
            for m in museums
        ]
    )

    prompt = f"""
    You are a museum ticket booking assistant , devloped by deepak j and gokul k. Use this data:
    be helpful and chatty
    
    User Query: {user_query}
    
    Respond in this format:
    Answer: [your response]
    Tickets: [number of tickets if booking, else 0]
    MuseumID: [museum ID if booking, else null]
    
    
    your past history:{
        history
    }



    this is the museum data you have :{    {museum_data}}
    """
    print("prompt:", prompt)
    return prompt


async def call_agent(user_query: str, db: Session):
    prompt = generate_gemini_prompt(user_query, db)
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = await model.generate_content_async(prompt)

        answer = ""
        tickets = 0
        museum_id = None
        for line in response.text.split("\n"):
            line = line.strip()
            if line.startswith("Answer: "):
                answer = line.replace("Answer: ", "").strip()
            elif line.startswith("Tickets: "):
                tickets_str = line.replace("Tickets: ", "").strip()
                tickets = int(tickets_str) if tickets_str.isdigit() else 0
            elif line.startswith("MuseumID: "):
                museum_id_str = line.replace("MuseumID: ", "").strip()
                museum_id = int(museum_id_str) if museum_id_str.isdigit() else None
        history.append(f"""User Query: {user_query}
        \n
        responose :{response.text}""")
        return Response(
            answer=answer, no_of_tickets=tickets, booked_museum_id=museum_id
        )
    except Exception as e:
        logger.error(f"Error in Gemini API call: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Payment Endpoints
@app.post("/make-payment")
async def make_payment(request: PaymentRequest, db: Session = Depends(Database.get_db)):
    try:
        db.begin()
        sender = (
            db.query(MockBank)
            .filter(MockBank.upi_id == request.sender_upi)
            .with_for_update()
            .first()
        )

        # Get admin account
        receiver = (
            db.query(MockBank)
            .filter(MockBank.is_admin)
            .with_for_update()
            .first()
        )

        if not sender:
            raise HTTPException(400, "Sender UPI not found")
        if not receiver:
            raise HTTPException(400, "Admin account not found")

        if sender.balance < request.amount:
            raise HTTPException(
                400, f"Insufficient balance. Available: ₹{sender.balance:.2f}"
            )

        sender.balance -= request.amount
        receiver.balance += request.amount
        db.commit()

        return {
            "status": "success",
            "new_balance": float(sender.balance),
            "receiver_upi": receiver.upi_id,
            "amount": float(request.amount),
        }

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Payment failed: {str(e)}")

# Museum Endpoints
@app.post("/query")
async def chat(
    request: str = Body(..., embed=True), db: Session = Depends(Database.get_db)
):
    if not request:
        raise HTTPException(status_code=400, detail="Please provide a valid query")
    try:
        response = await call_agent(request, db)
        return response.dict()
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------------------------------------------------------------
# Razorpay Integration Endpoints
# ---------------------------------------------------------------------

from fastapi import Body
@app.post("/create_order")
async def create_order(order_request: OrderRequest):
    # Log the received amount
    logger.info(f"Received amount: {order_request.amount}")

    order_data = {
        "amount": int(order_request.amount * 100),  # Convert rupees to paise and ensure it's an int
        "currency": "INR",
        "payment_capture": 1
    }
    try:
        order = razor_client.order.create(data=order_data)
        logger.info(f"Order created: {order}")
        return {"order": order}
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/capture_payment")
async def capture_payment(request: PaymentRequest):
    """
    Capture a Razorpay payment using the payment_id from Razorpay.
    The PaymentRequest should include:
      - payment_id: the Razorpay payment ID
      - amount: the amount in INR (will be converted to paise)
      - sender_upi: (optional, for internal tracking)
    """
    try:
        amount_in_paise = int(request.amount * 100)
        captured_payment = "caputre is done"
        logger.info(f"Payment captured: {captured_payment}")
        return {"status": "success", "payment": captured_payment}
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error capturing payment: {error_message}")
        if "already been captured" in error_message:
            raise HTTPException(
                status_code=400, detail="This payment has already been captured."
            )
        raise HTTPException(status_code=500, detail=error_message)


# ---------------------------------------------------------------------
# Other Endpoints (Account, Query, Booking)
# ---------------------------------------------------------------------
@app.get("/account/{upi_id}")
def get_account(upi_id: str, db: Session = Depends(Database.get_db)):
    account = db.query(MockBank).filter(MockBank.upi_id == upi_id).first()
    if not account:
        raise HTTPException(404, "Account not found")
    return {
        "upi_id": account.upi_id,
        "balance": float(account.balance),
        "is_admin": account.is_admin,
    }

@app.get("/pay_details")
def get_pay_details(museum_id: int, no_of_tickets: int, db: Session = Depends(Database.get_db)):
    museum = db.query(Museum).filter(Museum.museum_id == museum_id).first()
    if not museum:
        raise HTTPException(status_code=404, detail="Museum not found")
    if no_of_tickets > museum.total_tickets:
        raise HTTPException(status_code=400, detail=f"Only {museum.total_tickets} tickets available")
    total_price = Decimal(museum.price) * no_of_tickets
    return {
        "museum_id": museum.museum_id,
        "museum_name": museum.museum_name,
        "total_price": float(total_price),
        "tickets": no_of_tickets,
    }

@app.post("/confirm_booking")
async def confirm_booking(booking: BookingRequest, db: Session = Depends(Database.get_db)):
    logger.info(f"Incoming booking request: {booking.dict()}")
    admin_account = db.query(MockBank).filter(MockBank.is_admin).with_for_update().first()
    if not admin_account:
        logger.error("Admin account not found")
        raise HTTPException(status_code=400, detail="Admin account not found")
    user_account = db.query(MockBank).filter(MockBank.upi_id == booking.user_upi).with_for_update().first()
    if not user_account:
        logger.error(f"User account not found for UPI: {booking.user_upi}")
        raise HTTPException(status_code=400, detail="User account not found")
    museum = db.query(Museum).get(booking.museum_id)
    if not museum:
        logger.error(f"Museum not found for ID: {booking.museum_id}")
        raise HTTPException(status_code=404, detail="Museum not found")
    if booking.tickets > museum.total_tickets:
        logger.error(f"Not enough tickets available. Requested: {booking.tickets}, Available: {museum.total_tickets}")
        raise HTTPException(status_code=400, detail=f"Only {museum.total_tickets} tickets available")
    total_price = Decimal(museum.price) * booking.tickets
    if user_account.balance < total_price:
        logger.error(f"Insufficient balance. Available: {user_account.balance}, Required: {total_price}")
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Available: ₹{user_account.balance:.2f}")
    user_account.balance -= total_price
    admin_account.balance += total_price
    museum.total_tickets -= booking.tickets
    db.commit()
    booking_details = {
        "museum_name": museum.museum_name,
        "tickets": booking.tickets,
        "total_price": float(total_price),
        "admin_upi": admin_account.upi_id,
        "user_upi": booking.user_upi,
    }
    send_confirmation_email(booking.email, booking_details)
    logger.info(f"Booking confirmed: {booking_details}")
    return {
        "status": "booking_confirmed",
        "museum_id": museum.museum_id,
        "tickets_booked": booking.tickets,
        "remaining_tickets": museum.total_tickets,
    }




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
