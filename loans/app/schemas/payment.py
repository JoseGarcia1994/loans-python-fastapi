# 📦 Standard library
from datetime import date

# 🌐 Third-party
from pydantic import BaseModel, Field

# 📁 Local imports

# This validates automatically the model
class PaymentRequest(BaseModel):
    payment: int = Field(gt=0)
    payment_date: date
    paid: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "payment": 1,
                "payment_date": "2026-04-25",
                "paid": False
            }
        }
    }

# Only transfers object to JSON
class PaymentResponse(BaseModel):
    payment_number: int
    payment_date: date
    paid: bool

    class Config:
        from_attributes = True