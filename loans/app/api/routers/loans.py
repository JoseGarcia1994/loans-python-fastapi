from fastapi import Path, HTTPException, Query, APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from starlette import status

from ..deps import db_dependency
from ...db.models import Loan, Payment
from datetime import date

from ...schemas.loan import LoanRequest
from ...services.loan_service import generate_payment_schedule

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def get_loans(db: db_dependency):
    return db.query(Loan).options(joinedload(Loan.payments)).all()

@router.get("/loans/by-date", status_code=status.HTTP_200_OK)
async def get_loan_by_date(
        db: db_dependency,
        date: date = Query(..., description="Date in format YYYY-MM-DD"),
):
    loans = db.query(Loan).options(joinedload(Loan.payments)).filter(Loan.date == date).all()

    if not loans:
        raise HTTPException(status_code=404, detail="No loans found for this date")
    return loans

@router.post("/loans", status_code=status.HTTP_201_CREATED)
async def create_loan(db: db_dependency, loan_request: LoanRequest):
    try:
        new_loan = Loan(**loan_request.model_dump())

        db.add(new_loan)
        db.commit()
        db.refresh(new_loan)

        # Find next monday
        payment_dates = generate_payment_schedule(loan_request.date)

        for i, payment_date in enumerate(payment_dates):
            payment = Payment(
                payment_number=i + 1,
                payment_date=payment_date,
                paid=False,
                loan_id=new_loan.id
            )

            db.add(payment)

        db.commit()

        return new_loan

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error creating loan"
        )

@router.put("/loans/{loan_id}", response_model=LoanRequest | None, status_code=status.HTTP_200_OK)
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

    # Find next monday
    payment_dates = generate_payment_schedule(loan.date)

    payments = db.query(Payment).filter(Payment.loan_id == loan_model.id).all()

    for i, payment in enumerate(payments):
        payment.payment_date = payment_dates[i]

    db.commit()


@router.delete("/loans/{loan_id}",  status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(db: db_dependency, loan_id: int = Path(gt=0)):

    loan = db.query(Loan).filter(Loan.id == loan_id).first()

    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    try:
        db.delete(loan)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting loan")