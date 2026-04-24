from typing import Optional

from fastapi import FastAPI, Path, HTTPException
from pydantic import BaseModel, Field

from datetime import date

from starlette import status

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
    Loan(id=2, name="Liam Garcia", amount=100, date=date(2021, 1, 10)),
    Loan(id=3, name="Adalynn Garcia", amount=100, date=date(2021, 3, 10)),
]

@app.get("/loans", status_code=status.HTTP_200_OK)
async def get_loans():
    return LOANS

@app.get("/loans/by-date", status_code=status.HTTP_200_OK)
async def get_loan_by_date(date: date):
    result = [loan for loan in LOANS if loan.date == date]

    if not result:
        raise HTTPException(status_code=404, detail="loan not found")

    return result

@app.post("/loans", status_code=status.HTTP_201_CREATED)
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

@app.put("/loans/{loan_id}", response_model=LoanRequest | None, status_code=status.HTTP_200_OK)
async def update_loan( loan: LoanRequest, loan_id: int = Path(gt=0)):
    for index, existing_loan in enumerate(LOANS):
        if existing_loan.id == loan_id:
            updated_loan = Loan(
                id=loan_id,
                name=loan.name,
                amount=loan.amount,
                date=loan.date
            )
            LOANS[index] = updated_loan
            return

    raise HTTPException(status_code=404, detail="Loan not found")

@app.delete("/loans/{loan_id}",  status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(loan_id: int = Path(gt=0)):
    for index, existing_loan in enumerate(LOANS):
        if existing_loan.id == loan_id:
            LOANS.pop(index)
            return

    raise HTTPException(status_code=404, detail="Loan not found")