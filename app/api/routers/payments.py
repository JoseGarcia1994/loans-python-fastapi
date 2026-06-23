# 📦 Standard library
from datetime import date, timedelta

# 🌐 Third-party
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from starlette import status

# 📁 Local imports
from ..deps import db_dependency, user_dependency
from ...db.models import Payment, Loan, Client
from ...services.loyalty_service import (
    calculate_payment_points,
    apply_points,
    update_late_streak,
)

router = APIRouter(
    tags=["payments"],
)

@router.patch(
    "/{payment_id}/pay",
    status_code=status.HTTP_200_OK,
)
async def pay_payment(
    user: user_dependency,
    db: db_dependency,
    payment_id: int = Path(gt=0),
):

    payment = (
        db.query(Payment)
        .options(
            joinedload(Payment.loan)
            .joinedload(Loan.client)
        )
        .filter(
            Payment.payment_id == payment_id
        )
        .first()
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    client = payment.loan.client

    if client.owner_id != user.get("id"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    if payment.paid:
        raise HTTPException(
            status_code=400,
            detail="Payment already paid"
        )

    try:

        points = calculate_payment_points(
            payment
        )

        payment.paid = True

        apply_points(
            client,
            points,
        )

        update_late_streak(
            client,
            points,
        )

        db.commit()

        return {
            "message": "Payment marked as paid",
            "points": points,
            "total_points": client.loyalty_points,
        }

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error updating payment",
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

    payments = (
        db.query(Payment)
        .options(
            joinedload(Payment.loan)
            .joinedload(Loan.client)
        )
        .join(Loan)
        .join(Client)
        .filter(
            Client.owner_id == user.get("id"),
            Payment.payment_date >= start_of_week,
            Payment.payment_date <= end_of_week,
        )
        .order_by(
            Payment.payment_date
        )
        .all()
    )

    result = []

    for payment in payments:
        result.append({
            "loan_id": payment.loan.id,
            "client_name":
                f"{payment.loan.client.first_name} "
                f"{payment.loan.client.last_name}",
            "payment_id": payment.payment_id,
            "payment_number": payment.payment_number,
            "payment_date": payment.payment_date,
            "payment_amount": payment.payment_amount,
            "paid": payment.paid,
        })

    return {
        "week_start": start_of_week,
        "week_end": end_of_week,
        "payments": result
    }