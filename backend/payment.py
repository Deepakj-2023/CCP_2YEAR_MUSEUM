import logging
import os
import smtplib
from decimal import Decimal
from email.mime.text import MIMEText
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import DECIMAL, Boolean, Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from database.database import Database
# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Setup
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:19141914@localhost/Deepak_WWW"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Gemini Configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Email Configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


# Database Models
class MockBank(Base):
    __tablename__ = "bankaccounts"
    upi_id = Column(String, primary_key=True)
    account_holder_name = Column(String(100), nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    balance = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    is_admin = Column(Boolean, default=False)


class Museum(Base):
    __tablename__ = "museums"
    museum_id = Column(Integer, primary_key=True, index=True)
    museum_name = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255), nullable=False)
    available_time = Column(String(50), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    total_tickets = Column(Integer, nullable=False)
    recommended_pick_time = Column(String(50), nullable=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class PaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    sender_upi: str = Field(..., min_length=3)
    receiver_upi: str = Field(..., min_length=3)
    transaction_id: str = Field(..., min_length=3)


class Response(BaseModel):
    answer: str
    no_of_tickets: int = 0
    booked_museum_id: Optional[int] = None


class BookingRequest(BaseModel):
    museum_id: int
    tickets: int
    user_upi: str
    transaction_id: str
    email: EmailStr


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Email Function
def send_confirmation_email(email: str, booking_details: dict):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logger.warning("Email credentials missing - skipping email send")
        return

    msg = MIMEText(f"""
    Booking Confirmed!
    
    Museum: {booking_details['museum_name']}
    Tickets: {booking_details['tickets']}
    Total Paid: ₹{booking_details['total_price']:.2f}
    Payment UPI ID: {booking_details['admin_upi']}
    Your UPI ID: {booking_details['user_upi']}
    Transaction ID: {booking_details['transaction_id']}
    
    Thank you for your booking!
    """)

    msg["Subject"] = "Museum Booking Confirmation"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        logger.info(f"Confirmation email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")


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
    You are a museum ticket booking assistant. Use this data:
    {museum_data}
    
    User Query: {user_query}
    
    Respond in this format:
    Answer: [your response]
    Tickets: [number of tickets if booking, else 0]
    MuseumID: [museum ID if booking, else null]
    """
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

        return Response(
            answer=answer, no_of_tickets=tickets, booked_museum_id=museum_id
        )
    except Exception as e:
        logger.error(f"Error in Gemini API call: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoints
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


@app.get("/pay_details")
def get_pay_details(
    museum_id: int, no_of_tickets: int, db: Session = Depends(Database.get_db)
):
    museum = db.query(Museum).filter(Museum.museum_id == museum_id).first()
    if not museum:
        raise HTTPException(status_code=404, detail="Museum not found")

    if no_of_tickets > museum.total_tickets:
        raise HTTPException(
            status_code=400, detail=f"Only {museum.total_tickets} tickets available"
        )

    total_price = Decimal(museum.price) * no_of_tickets

    return {
        "museum_id": museum.museum_id,
        "museum_name": museum.museum_name,
        "total_price": float(total_price),
        "tickets": no_of_tickets,
    }


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

        receiver = (
            db.query(MockBank)
            .filter(MockBank.upi_id == request.receiver_upi)
            .with_for_update()
            .first()
        )

        if not sender:
            raise HTTPException(400, "Sender UPI not found")
        if not receiver:
            raise HTTPException(400, "Receiver UPI not found")
        if not receiver.is_admin:
            raise HTTPException(400, "Can only pay to admin account")

        if sender.balance < request.amount:
            raise HTTPException(
                400, f"Insufficient balance. Available: ₹{sender.balance:.2f}"
            )

        sender.balance -= request.amount
        receiver.balance += request.amount
        db.commit()

        return {
            "status": "success",
            "transaction_id": request.transaction_id,
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
        raise HTTPException(500, "Payment processing error")


@app.post("/confirm_booking")
async def confirm_booking(
    booking: BookingRequest, db: Session = Depends(Database.get_db)
):
    museum = db.query(Museum).get(booking.museum_id)
    if not museum:
        raise HTTPException(status_code=404, detail="Museum not found")

    if booking.tickets > museum.total_tickets:
        raise HTTPException(
            status_code=400, detail=f"Only {museum.total_tickets} tickets available"
        )

    admin_account = db.query(MockBank).filter(MockBank.is_admin).first()

    booking_details = {
        "museum_name": museum.museum_name,
        "tickets": booking.tickets,
        "total_price": float(museum.price * booking.tickets),
        "admin_upi": admin_account.upi_id,
        "user_upi": booking.user_upi,
        "transaction_id": booking.transaction_id,
    }

    museum.total_tickets -= booking.tickets
    db.commit()

    send_confirmation_email(booking.email, booking_details)

    return {
        "status": "booking_confirmed",
        "museum_id": museum.museum_id,
        "tickets_booked": booking.tickets,
        "remaining_tickets": museum.total_tickets,
    }


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
