from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import logging

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

# Database Connection
DATABASE_URL = "postgresql://postgres:19141914@localhost/museum_bookings_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI App
app = FastAPI()

# Enable CORS to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Museum Model
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

# Create tables (only needed once)
Base.metadata.create_all(engine)

# Dependency: Get Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoint: Fetch all museums
@app.get("/museums")
def get_museums(db: Session = Depends(get_db)):
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
