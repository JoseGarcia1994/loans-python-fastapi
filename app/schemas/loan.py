# 📦 Standard library
from datetime import date

# 🌐 Third-party
from pydantic import BaseModel, Field

class LoanBase(BaseModel):

    client_id: int = Field(
        gt=0,
        description="Client id"
    )

    amount: int = Field(
        ge=1000,
        description="Loan amount must be at least 1000"
    )

    date: date

    model_config = {
        "json_schema_extra": {
            "example": {
                "client_id": 1,
                "amount": 1000,
                "date": "2026-06-17"
            }
        }
    }


class LoanRequest(LoanBase):
    pass


class UpdateLoanRequest(LoanBase):
    pass