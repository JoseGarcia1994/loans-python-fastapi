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

    def __init__(self,id, name, amount, date):
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
    Loan(id=1, name="Jose Garcia", amount=100, date=date(2021, 1, 10)),
    Loan(id=2, name="Liam Garcia", amount=100, date=date(2021, 2, 10)),
    Loan(id=3, name="Adalynn Garcia", amount=100, date=date(2021, 3, 10)),
]

@app.get("/loans")
async def get_loans():
    return LOANS

@app.get("/loans/{loan_date}")
async def get_loan_by_date(loan_date: date):
    for loan in LOANS:
        if loan.date == loan_date:
            return loan

@app.post("/loans")
async def create_loan(loan_request: LoanRequest):
    new_loan = Loan(**loan_request.model_dump())
    LOANS.append(find_loan_id(new_loan))
    return new_loan

def find_loan_id(loan: Loan):
    if LOANS:
        max_id = max(l.id for l in LOANS)
        loan.id = max_id + 1
    else:
        loan.id = 1
    return loan

@app.put("/loans/{loan_id}", response_model=LoanRequest | None)
async def update_loan(loan_id: int, loan: LoanRequest):
    for index, existing_loan in enumerate(LOANS):
        if existing_loan.id == loan_id:
            updated_loan = Loan(
                id=loan_id,
                name=loan.name,
                amount=loan.amount,
                date=loan.date
            )
            LOANS[index] = updated_loan
            return updated_loan

    return None