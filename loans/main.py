from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from datetime import date

app = FastAPI()

class Loan:
    id: int
    name: str
    amount: int
    date: str

    def __init__(self,id,name,amount,date):
        self.id = id
        self.name = name
        self.amount = amount
        self.date = date

class LoanRequest(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=3, max_length=24)
    amount: int = Field(gt=-1)
    date: date

    model_config = {
        "json_schema": {
            "example": {
                "name": "name of loan",
                "amount": 100,
                "date": "2021-01-10"
            }
        }
    }

LOANS = [
    Loan(id=1,name="Jose Garcia",amount=100,date="2021-01-10"),
    Loan(id=2,name="Liam Garcia",amount=100,date="2021-01-10"),
    Loan(id=3,name="Adalynn Garcia",amount=100,date="2021-01-10"),
]

@app.get("/loans")
async def get_loans():
    return LOANS

@app.post("/create_loan")
async def create_loan(loan_request: LoanRequest):
    new_loan = Loan(**loan_request.model_dump())
    LOANS.append(find_loan_id(new_loan))

def find_loan_id(loan: Loan):
    if LOANS:
        max_id = max(l.id for l in LOANS)
        loan.id = max_id + 1
    else:
        loan.id = 1
    return loan
