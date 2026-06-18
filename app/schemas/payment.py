# 📦 Standard library
from datetime import date

# 🌐 Third-party
from pydantic import BaseModel, ConfigDict

class PaymentResponse(BaseModel):

    payment_id: int

    payment_number: int

    payment_amount: int

    payment_date: date

    paid: bool

    loan_id: int

    model_config = ConfigDict(
        from_attributes=True
    )