
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
# Pydantic Models

class PaymentRequest(BaseModel):
    payment_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    sender_upi: str = Field(..., min_length=3)


class Response(BaseModel):
    answer: str
    no_of_tickets: int = 0
    booked_museum_id: Optional[int] = None


class BookingRequest(BaseModel):
    museum_id: int
    tickets: int
    user_upi: str
    email: EmailStr
class OrderRequest(BaseModel):
    amount: float
