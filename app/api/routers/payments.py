# 📦 Standard library
from datetime import date, timedelta

# 🌐 Third-party
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from starlette import status

# 📁 Local imports
from ..deps import db_dependency, user_dependency
from ...db.models import Payment, Loan

router = APIRouter(
    tags=["payments"],
)

@router.patch("/{payment_id}/pay", status_code=status.HTTP_200_OK)
async def pay_payment(
    user: user_dependency,
    db: db_dependency,
    payment_id: int = Path(gt=0)
):
    payment = db.query(Payment).filter(
        Payment.payment_id == payment_id
    ).first()

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    loan = db.query(Loan).filter(
        Loan.id == payment.loan_id,
        Loan.owner_id == user.get("id")
    ).first()

    if loan is None:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    try:
        payment.paid = True

        db.commit()

        return {
            "message": "Payment marked as paid"
        }

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error updating payment"
        )

@router.get("/week", status_code=status.HTTP_200_OK)
async def get_payments_by_week(
    user: user_dependency,
    db: db_dependency,
    offset: int = 0
):

    # Current date
    today = date.today()

    # Get monday of current week
    start_of_week = today - timedelta(days=today.weekday())

    # Move week depending on offset
    start_of_week = start_of_week + timedelta(weeks=offset)

    # Get sunday
    end_of_week = start_of_week + timedelta(days=6)

    payments = db.query(Payment).options(
        joinedload(Payment.loan)
    ).join(Loan).filter(
        Loan.owner_id == user.get("id"),
        Payment.payment_date >= start_of_week,
        Payment.payment_date <= end_of_week,
    ).order_by(
        Payment.payment_date
    ).all()

    result = []

    for payment in payments:

        result.append({
            "loan_id": payment.loan.id,
            "loan_name": payment.loan.name,
            "payment_id": payment.payment_id,
            "payment_number": payment.payment_number,
            "payment_date": payment.payment_date,
            "payment_amount": payment.loan.amount / 10,
            "paid": payment.paid
        })

    return {
        "week_start": start_of_week,
        "week_end": end_of_week,
        "payments": result
    }