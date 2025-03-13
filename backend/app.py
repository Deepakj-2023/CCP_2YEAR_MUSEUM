from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:19141914@localhost/museum_bookings_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Gemini Configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    request: str

class ChatResponse(BaseModel):
    answer: str
    no_of_tickets: int = 0
    booked_museum_id: Optional[int] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_gemini_prompt(user_query: str, db: Session):
    print("Generating prompt for user query:", user_query)
    museums = db.query(Museum).all()
    museum_data = "\n".join([f"""
    Museum ID: {m.museum_id}
    Name: {m.museum_name}
    Location: {m.location}
    Price: {m.price}
    Available Tickets: {m.total_tickets}
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
    print("Generated Prompt:\n", prompt)
    return prompt

# Update the response parsing section in the /query endpoint
@app.post("/query")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        print("Received chat request:", request.request)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = generate_gemini_prompt(request.request, db)
        response = await model.generate_content_async(prompt)
        print("Gemini Response:", response.text)
        
        # Parse Gemini response
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
                museum_id_str = line.replace("MuseumID: ", "").strip().lower()
                museum_id = int(museum_id_str) if museum_id_str.isdigit() else None

        print("Parsed Response:", answer, tickets, museum_id)
        
        return {
            "answer": answer,
            "no_of_tickets": tickets,
            "booked_museum_id": museum_id
        }
    except Exception as e:
        print("Error in /query endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pay_details")
def get_pay_details(museum_id: int, no_of_tickets: int, db: Session = Depends(get_db)):
    try:
        print(f"Fetching payment details for Museum ID: {museum_id}, Tickets: {no_of_tickets}")
        museum = db.query(Museum).filter(Museum.museum_id == museum_id).first()
        
        if not museum:
            print("Museum not found")
            raise HTTPException(status_code=404, detail="Museum not found")
        
        total = float(museum.price) * no_of_tickets
        
        print("Payment Details:", {
            "museum_name": museum.museum_name,
            "price": float(museum.price),
            "total": total,
            "tickets": no_of_tickets
        })
        
        return {
            "museum_name": museum.museum_name,
            "price": float(museum.price),
            "total": total,
            "tickets": no_of_tickets
        }
    except Exception as e:
        print("Error in /pay_details endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e))