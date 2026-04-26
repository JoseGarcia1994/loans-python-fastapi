from typing import Optional

from pydantic import BaseModel, Field

from datetime import date

# This validates automatically the model
class LoanRequest(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=3, max_length=24)
    amount: int = Field(ge=1000, description="Loan amount must be at least 1000")
    date: date

    model_config = {
        "json_schema": {
            "example": {
                "name": "name of loan",
                "amount": 1000,
                "date": "2021-01-10"
            }
        }
    }
