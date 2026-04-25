from typing import Optional, Annotated

from fastapi import FastAPI, Path, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from datetime import date

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
import models
from models import Loan
from database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

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

@app.get("/", status_code=status.HTTP_200_OK)
async def get_loans(db: db_dependency):
    return db.query(Loan).all()

@app.get("/loans/by-date", status_code=status.HTTP_200_OK)
async def get_loan_by_date(
        db: db_dependency,
        date: date = Query(..., description="Date in format YYYY-MM-DD"),
):
    loans = db.query(Loan).filter(Loan.date == date).all()

    if not loans:
        raise HTTPException(status_code=404, detail="No loans found for this date")
    return loans

@app.post("/loans", status_code=status.HTTP_201_CREATED)
async def create_loan(db: db_dependency, loan_request: LoanRequest):
    try:
        new_loan = Loan(**loan_request.model_dump())

        db.add(new_loan)
        db.commit()
        db.refresh(new_loan)

        return new_loan

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error creating loan"
        )

@app.put("/loans/{loan_id}", response_model=LoanRequest | None, status_code=status.HTTP_200_OK)
async def update_loan(
        db: db_dependency,
        loan: LoanRequest,
        loan_id: int = Path(gt=0)
):
    loan_model = db.query(Loan).filter(Loan.id == loan_id).first()

    if loan_model is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    update_data = loan.model_dump(exclude={"id"})

    for key, value in update_data.items():
        setattr(loan_model, key, value)

    db.commit()
    db.refresh(loan_model)

    return loan_model


@app.delete("/loans/{loan_id}",  status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(loan_id: int = Path(gt=0)):
    for index, existing_loan in enumerate(LOANS):
        if existing_loan.id == loan_id:
            LOANS.pop(index)
            return

    raise HTTPException(status_code=404, detail="Loan not found")