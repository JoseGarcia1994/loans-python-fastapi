# 📦 Standard library
from datetime import date

# 🌐 Third-party
from fastapi import Path, HTTPException, Query, APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from starlette import status

# 📁 Local imports
from ..deps import db_dependency, user_dependency
from ...db.models import Loan, Payment
from ...schemas.loan import LoanRequest, UpdateLoanRequest
from ...services.loan_service import generate_payment_schedule

router = APIRouter(tags=["loan"])

@router.get("/", status_code=status.HTTP_200_OK)
async def get_loans(user: user_dependency, db: db_dependency):
    return db.query(Loan).options(joinedload(Loan.payments)).filter(Loan.owner_id == user.get("id")).all()

@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_dashboard_stats(user: user_dependency, db: db_dependency):

    loans = (
        db.query(Loan)
        .options(joinedload(Loan.payments))
        .filter(Loan.owner_id == user.get("id"))
        .all()
    )

    total_loans = len(loans)
    total_lent = sum(loan.amount for loan in loans)

    active_loans = 0
    pending_payments_count = 0
    paid_payments_count = 0
    pending_amount = 0

    for loan in loans:

        pending_payments = [p for p in loan.payments if not p.paid]
        paid_payments = [p for p in loan.payments if p.paid]

        if pending_payments:
            active_loans += 1

        pending_payments_count += len(pending_payments)
        paid_payments_count += len(paid_payments)

        pending_amount += sum(
            payment.payment_amount
            for payment in pending_payments
        )

    return {
        "total_loans": total_loans,
        "active_loans": active_loans,
        "total_lent": total_lent,
        "pending_payments": pending_payments_count,
        "paid_payments": paid_payments_count,
        "pending_amount": round(pending_amount, 2),
    }

@router.get("/{loan_id}", status_code=status.HTTP_200_OK)
async def get_loan_by_id(
        user: user_dependency,
        db: db_dependency,
        loan_id: int = Path(gt=0),
):
    loan = db.query(Loan).options(
        joinedload(Loan.payments)
    ).filter(
        Loan.id == loan_id,
        Loan.owner_id == user.get("id")
    ).first()

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    return loan

@router.get("/by-date", status_code=status.HTTP_200_OK)
async def get_loan_by_date(
        user: user_dependency,
        db: db_dependency,
        date: date = Query(..., description="Date in format YYYY-MM-DD"),
):
    loans = db.query(Loan).options(
        joinedload(Loan.payments)
    ).filter(
        Loan.date == date,
        Loan.owner_id == user.get("id")
    ).all()

    if not loans:
        raise HTTPException(status_code=404, detail="No loans found for this date")
    return loans

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_loan(user: user_dependency,
                      db: db_dependency,
                      loan_request: LoanRequest
                      ):
    try:
        new_loan = Loan(**loan_request.model_dump(), owner_id=user.get("id"))

        db.add(new_loan)
        db.commit()
        db.refresh(new_loan)

        # Find next monday
        payment_dates = generate_payment_schedule(loan_request.date)

        payment_amount = int(
            loan_request.amount * 0.10
        )

        for i, payment_date in enumerate(payment_dates):
            payment = Payment(
                payment_number=i + 1,
                payment_amount=payment_amount,
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
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating loan"
        )

@router.put("/{loan_id}", response_model=LoanRequest | None, status_code=status.HTTP_200_OK)
async def update_loan(
        user: user_dependency,
        db: db_dependency,
        loan: UpdateLoanRequest,
        loan_id: int = Path(gt=0)
):
    loan_model = db.query(Loan).filter(Loan.id == loan_id, Loan.owner_id == user.get("id")).first()

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

    payment_amount = int(
        loan.amount * 0.10
    )

    for i, payment in enumerate(payments):
        payment.payment_date = payment_dates[i]
        payment.payment_amount = payment_amount

    db.commit()

    return loan_model


@router.delete("/{loan_id}",  status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(user: user_dependency, db: db_dependency, loan_id: int = Path(gt=0)):

    loan = db.query(Loan).filter(Loan.id == loan_id, Loan.owner_id == user.get("id")).first()

    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    try:
        db.delete(loan)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting loan")