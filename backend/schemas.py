from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
# Pydantic Models
class PaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
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
