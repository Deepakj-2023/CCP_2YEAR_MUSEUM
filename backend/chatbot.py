# from fastapi import FastAPI, Depends, HTTPException, Body
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from pydantic import BaseModel, Field
# from typing import Optional
# import google.generativeai as genai
# from dotenv import load_dotenv
# import os
# import logging

# # Load environment variables
# load_dotenv()

# # Logger setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Database Setup
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:19141914@localhost/museum_bookings_db")
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # Gemini Configuration
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# # Database Models
# class Museum(Base):
#     __tablename__ = "museums"
#     museum_id = Column(Integer, primary_key=True, index=True)
#     museum_name = Column(String(255), nullable=False)
#     description = Column(Text)
#     location = Column(String(255), nullable=False)
#     available_time = Column(String(50), nullable=False)
#     price = Column(DECIMAL(10, 2), nullable=False)
#     total_tickets = Column(Integer, nullable=False)
#     recommended_pick_time = Column(String(50), nullable=False)

# class Booking(Base):
#     __tablename__ = "bookings"
#     id = Column(Integer, primary_key=True, index=True)
#     museum_id = Column(Integer, ForeignKey('museums.museum_id'))
#     tickets = Column(Integer)
#     total_price = Column(DECIMAL(10, 2))

# Base.metadata.create_all(bind=engine)

# # FastAPI app initialization
# app = FastAPI()

# # CORS Middleware Setup
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Pydantic Models for Response Validation
# class Response(BaseModel):
#     answer: str = Field(min_length=3)
#     no_of_tickets: int = Field(ge=0, le=10)
#     booked_museum_id: Optional[int] = None

# # Database Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Generate Prompt for Gemini API
# def generate_gemini_prompt(user_query: str, db: Session):
#     logger.info(f"Generating prompt for user query: {user_query}")
#     museums = db.query(Museum).all()
#     museum_data = "\n".join([f"""
#     Museum ID: {m.museum_id}
#     Name: {m.museum_name}
#     Location: {m.location}
#     Description: {m.description}
#     Price: {m.price}
#     Available Tickets: {m.total_tickets}
#     Available Time: {m.available_time}
#     Recommended Pick Time: {m.recommended_pick_time}
#     """ for m in museums])
    
#     prompt = f"""
#     You are a museum ticket booking assistant. Use this data:
#     {museum_data}
    
#     User Query: {user_query}
    
#     Respond in this format:
#     Answer: [your response]
#     Tickets: [number of tickets if booking, else 0]
#     MuseumID: [museum ID if booking, else null]
#     """
#     return prompt

# # Call Gemini API asynchronously
# async def call_agent(user_query: str, db: Session):
#     prompt = generate_gemini_prompt(user_query, db)
#     model = genai.GenerativeModel('gemini-1.5-flash')
#     try:
#         response = await model.generate_content_async(prompt)
#         logger.info(f"Gemini Response: {response.text}")
        
#         answer = ""
#         tickets = 0
#         museum_id = None
#         for line in response.text.split('\n'):
#             line = line.strip()
#             if line.startswith("Answer: "):
#                 answer = line.replace("Answer: ", "").strip()
#             elif line.startswith("Tickets: "):
#                 tickets_str = line.replace("Tickets: ", "").strip()
#                 tickets = int(tickets_str) if tickets_str.isdigit() else 0
#             elif line.startswith("MuseumID: "):
#                 museum_id_str = line.replace("MuseumID: ", "").strip()
#                 museum_id = int(museum_id_str) if museum_id_str.isdigit() else None
        
#         return Response(answer=answer, no_of_tickets=tickets, booked_museum_id=museum_id)
#     except Exception as e:
#         logger.error(f"Error in Gemini API call: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# # Chatbot Endpoint
# @app.post("/query")
# async def chat(request: str = Body(..., embed=True), db: Session = Depends(get_db)):
#     if not request:
#         raise HTTPException(status_code=400, detail="Please provide a valid query")
#     try:
#         response = await call_agent(request, db)
#         return response.dict()
#     except Exception as e:
#         logger.error(f"Error in chat: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# # Payment Details Endpoint
# @app.get("/pay_details")
# def get_pay_details(museum_id: int, no_of_tickets: int, db: Session = Depends(get_db)):
#     if no_of_tickets <= 0:
#         raise HTTPException(status_code=400, detail="Number of tickets must be greater than zero")
    
#     museum = db.query(Museum).filter(Museum.museum_id == museum_id).first()
#     if not museum:
#         raise HTTPException(status_code=404, detail="Museum not found")
    
#     total_cost = float(museum.price) * no_of_tickets
#     return {
#         "museum_id": museum.museum_id,
#         "museum_name": museum.museum_name,
#         "location": museum.location,
#         "description": museum.description,
#         "available_time": museum.available_time,
#         "recommended_pick_time": museum.recommended_pick_time,
#         "price_per_ticket": float(museum.price),
#         "total_cost": total_cost,
#         "no_of_tickets": no_of_tickets
#     }


# ################## update version
# from fastapi import FastAPI, Depends, HTTPException, Body
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from pydantic import BaseModel, Field
# from typing import Optional
# import google.generativeai as genai
# from dotenv import load_dotenv
# import os
# import logging

# # Load environment variables
# load_dotenv()

# # Logger setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Database Setup
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:19141914@localhost/museum_bookings_db")
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # Gemini Configuration
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# # Database Models
# class Museum(Base):
#     __tablename__ = "museums"
#     museum_id = Column(Integer, primary_key=True, index=True)
#     museum_name = Column(String(255), nullable=False)
#     description = Column(Text)
#     location = Column(String(255), nullable=False)
#     available_time = Column(String(50), nullable=False)
#     price = Column(DECIMAL(10, 2), nullable=False)
#     total_tickets = Column(Integer, nullable=False)
#     recommended_pick_time = Column(String(50), nullable=False)
 
# Base.metadata.create_all(bind=engine)

# # FastAPI app initialization
# app = FastAPI()

# # CORS Middleware Setup
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Pydantic Models for Response Validation
# class Response(BaseModel):
#     answer: str = Field(min_length=3)
#     no_of_tickets: int = Field(ge=0, le=10)
#     booked_museum_id: Optional[int] = None

# # Database Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Generate Prompt for Gemini API
# def generate_gemini_prompt(user_query: str, db: Session):
#     logger.info(f"Generating prompt for user query: {user_query}")
#     museums = db.query(Museum).all()
#     museum_data = "\n".join([f"""
#     Museum ID: {m.museum_id}
#     Name: {m.museum_name}
#     Location: {m.location}
#     Description: {m.description}
#     Price: {m.price}
#     Available Tickets: {m.total_tickets}
#     Available Time: {m.available_time}
#     Recommended Pick Time: {m.recommended_pick_time}
#     """ for m in museums])
    
#     prompt = f"""
#     You are a museum ticket booking assistant. Use this data:
#     {museum_data}
    
#     User Query: {user_query}
    
#     Respond in this format:
#     Answer: [your response]
#     Tickets: [number of tickets if booking, else 0]
#     MuseumID: [museum ID if booking, else null]
#     """
#     return prompt

# # Call Gemini API asynchronously
# async def call_agent(user_query: str, db: Session):
#     prompt = generate_gemini_prompt(user_query, db)
#     model = genai.GenerativeModel('gemini-1.5-flash')
#     try:
#         response = await model.generate_content_async(prompt)
#         logger.info(f"Gemini Response: {response.text}")
        
#         answer = ""
#         tickets = 0
#         museum_id = None
#         for line in response.text.split('\n'):
#             line = line.strip()
#             if line.startswith("Answer: "):
#                 answer = line.replace("Answer: ", "").strip()
#             elif line.startswith("Tickets: "):
#                 tickets_str = line.replace("Tickets: ", "").strip()
#                 tickets = int(tickets_str) if tickets_str.isdigit() else 0
#             elif line.startswith("MuseumID: "):
#                 museum_id_str = line.replace("MuseumID: ", "").strip()
#                 museum_id = int(museum_id_str) if museum_id_str.isdigit() else None
        
#         return Response(answer=answer, no_of_tickets=tickets, booked_museum_id=museum_id)
#     except Exception as e:
#         logger.error(f"Error in Gemini API call: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# # Chatbot Endpoint
# @app.post("/query")
# async def chat(request: str = Body(..., embed=True), db: Session = Depends(get_db)):
#     if not request:
#         raise HTTPException(status_code=400, detail="Please provide a valid query")
#     try:
#         response = await call_agent(request, db)
#         return response.dict()
#     except Exception as e:
#         logger.error(f"Error in chat: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")

# # Payment Details Endpoint
# @app.get("/pay_details")
# def get_pay_details(museum_id: int, no_of_tickets: int, db: Session = Depends(get_db)):
#     if no_of_tickets <= 0:
#         raise HTTPException(status_code=400, detail="Number of tickets must be greater than zero")
    
#     museum = db.query(Museum).filter(Museum.museum_id == museum_id).first()
#     if not museum:
#         raise HTTPException(status_code=404, detail="Museum not found")
    
#     total_cost = float(museum.price) * no_of_tickets
#     return {
#         "museum_id": museum.museum_id,
#         "museum_name": museum.museum_name,
#         "location": museum.location,
#         "description": museum.description,
#         "available_time": museum.available_time,
#         "recommended_pick_time": museum.recommended_pick_time,
#         "price_per_ticket": float(museum.price),
#         "total_cost": total_cost,
#         "no_of_tickets": no_of_tickets
#     }

# #############  
###### updation process 

#### this code is taken by the  app.py okay 
### for the paymnet module integeration


from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
import os
import logging
import smtplib
from email.mime.text import MIMEText

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:19141914@localhost/museum_bookings_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Gemini Configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Email Configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Database Models
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

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    museum_id = Column(Integer, ForeignKey('museums.museum_id'))
    tickets = Column(Integer)
    total_price = Column(DECIMAL(10, 2))
    user_email = Column(String(255))  # Added email field

Base.metadata.create_all(bind=engine)

# FastAPI app initialization
app = FastAPI()

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class Response(BaseModel):
    answer: str = Field(min_length=3)
    no_of_tickets: int = Field(ge=0, le=10)
    booked_museum_id: Optional[int] = None

class ConfirmBookingRequest(BaseModel):
    museum_id: int
    tickets: int = Field(..., gt=0)
    user_email: EmailStr
    upi_transaction_id: str = Field(..., min_length=3)

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
    Total Paid: ₹{booking_details['total_price']}
    Payment UPI ID: {os.getenv("ADMIN_UPI_ID", "admin_upi_id")}
    Transaction ID: {booking_details['upi_transaction_id']}
    
    Thank you for your booking!
    """)
    
    msg['Subject'] = 'Museum Booking Confirmation'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        logger.info(f"Confirmation email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

# Gemini Functions
def generate_gemini_prompt(user_query: str, db: Session):
    logger.info(f"Generating prompt for user query: {user_query}")
    museums = db.query(Museum).all()
    museum_data = "\n".join([f"""
    Museum ID: {m.museum_id}
    Name: {m.museum_name}
    Location: {m.location}
    Description: {m.description}
    Price: {m.price}
    Available Tickets: {m.total_tickets}
    Available Time: {m.available_time}
    Recommended Pick Time: {m.recommended_pick_time}
    """ for m in museums])
    
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
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = await model.generate_content_async(prompt)
        logger.info(f"Gemini Response: {response.text}")
        
        answer = ""
        tickets = 0
        museum_id = None
        for line in response.text.split('\n'):
            line = line.strip()
            if line.startswith("Answer: "):
                answer = line.replace("Answer: ", "").strip()
            elif line.startswith("Tickets: "):
                tickets_str = line.replace("Tickets: ", "").strip()
                tickets = int(tickets_str) if tickets_str.isdigit() else 0
            elif line.startswith("MuseumID: "):
                museum_id_str = line.replace("MuseumID: ", "").strip()
                museum_id = int(museum_id_str) if museum_id_str.isdigit() else None
        
        return Response(answer=answer, no_of_tickets=tickets, booked_museum_id=museum_id)
    except Exception as e:
        logger.error(f"Error in Gemini API call: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Endpoints
@app.post("/query")
async def chat(request: str = Body(..., embed=True), db: Session = Depends(get_db)):
    if not request:
        raise HTTPException(status_code=400, detail="Please provide a valid query")
    try:
        response = await call_agent(request, db)
        return response.dict()
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/pay_details")
def get_pay_details(museum_id: int, no_of_tickets: int, db: Session = Depends(get_db)):
    museum = db.query(Museum).filter(Museum.museum_id == museum_id).first()
    if not museum:
        raise HTTPException(status_code=404, detail="Museum not found")
    
    if no_of_tickets > museum.total_tickets:
        raise HTTPException(
            status_code=400,
            detail=f"Only {museum.total_tickets} tickets available"
        )

    total_price = float(museum.price) * no_of_tickets
    
    return {
        "payment_instructions": f"Send ₹{total_price} to UPI ID: {os.getenv('ADMIN_UPI_ID', 'admin_upi_id')}",
        "upi_id": os.getenv("ADMIN_UPI_ID", "admin_upi_id"),
        "museum_id": museum.museum_id,
        "museum_name": museum.museum_name,
        "total_price": total_price,
        "tickets": no_of_tickets
    }

@app.post("/confirm_booking")
async def confirm_booking(request: ConfirmBookingRequest, db: Session = Depends(get_db)):
    museum = db.query(Museum).filter(Museum.museum_id == request.museum_id).first()
    if not museum:
        raise HTTPException(status_code=404, detail="Museum not found")
    
    if request.tickets > museum.total_tickets:
        raise HTTPException(
            status_code=400,
            detail=f"Only {museum.total_tickets} tickets available"
        )
    
    total_price = float(museum.price) * request.tickets
    booking = Booking(
        museum_id=request.museum_id,
        tickets=request.tickets,
        total_price=total_price,
        user_email=request.user_email
    )

    try:
        museum.total_tickets -= request.tickets
        db.add_all([museum, booking])
        db.commit()
        db.refresh(booking)
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Booking failed")

    booking_details = {
        "museum_name": museum.museum_name,
        "tickets": request.tickets,
        "total_price": total_price,
        "upi_transaction_id": request.upi_transaction_id
    }

    send_confirmation_email(request.user_email, booking_details)

    return {
        "status": "success",
        "message": "Payment processed and booking confirmed",
        "booking_id": booking.id,
        "payment_details": {
            "upi_id": os.getenv("ADMIN_UPI_ID", "admin_upi_id"),
            "amount": total_price,
            "transaction_id": request.upi_transaction_id
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
