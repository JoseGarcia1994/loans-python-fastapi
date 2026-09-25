# 📦 Standard library
from datetime import date, datetime
from typing import Optional

# 🌐 Third-party
from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class PaymentOut(BaseModel):
    payment_id: int
    payment_number: int
    payment_amount: float
    payment_date: date
    paid: bool
    paid_at: Optional[datetime] = None
    loan_id: int
    model_config = ConfigDict(from_attributes=True)


class LoanOut(BaseModel):
    id: int
    amount: int
    start_date: date
    end_date: Optional[date] = None
    total_weeks: Optional[int] = None
    status: str
    is_completed: bool
    payments: list[PaymentOut] = []
    model_config = ConfigDict(from_attributes=True)


class ClientResponse(ClientBase):
    id: int
    loyalty_points: int
    reward_level: str
    is_active: bool
    created_at: datetime
    loans: list[LoanOut] = []
    model_config = ConfigDict(from_attributes=True)

# Forzar resolución de referencias anidadas en Pydantic v2
PaymentOut.model_rebuild()
LoanOut.model_rebuild()
ClientResponse.model_rebuild()