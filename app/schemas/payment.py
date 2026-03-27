from pydantic import BaseModel, Field
from typing import Optional, Dict
from decimal import Decimal

class PaymentCreate(BaseModel):
    amount: Decimal
    currency: str
    description: Optional[str] = None
    metadata: Optional[Dict] = None
    webhook_url: str


class PaymentResponse(BaseModel):
    id: str
    amount: Decimal
    currency: str
    status: str