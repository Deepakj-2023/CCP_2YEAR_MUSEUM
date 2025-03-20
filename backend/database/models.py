
# Database Models
from sqlalchemy import  Column, Integer, String, Text, DECIMAL, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
class MockBank(Base):
    __tablename__ = "bankaccounts"
    upi_id = Column(String, primary_key=True)
    account_holder_name = Column(String(100), name='accountholdername', nullable=False)
    phone_number = Column(String(15), name='phonenumber', unique=True, nullable=False)
    balance = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    is_admin = Column(Boolean, name='is_admin', default=False)  # <-- Updated here # <-- And here if needed

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
