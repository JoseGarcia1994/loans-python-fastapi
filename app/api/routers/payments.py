# 📦 Standard library
from datetime import date, timedelta, datetime

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
    update_late_streak, calculate_liquidation_points,
)
from ...services.loan_service import close_loan_if_completed

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
        payment.paid_at = datetime.now()

        apply_points(
            client,
            points,
        )

        update_late_streak(
            client,
            points,
        )

        db.commit()

        close_loan_if_completed(payment.loan, db)

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

@router.patch("/{loan_id}/liquidate", status_code=status.HTTP_200_OK)
async def liquidate_loan(
    user: user_dependency,
    db: db_dependency,
    loan_id: int = Path(gt=0),
):
    loan = (
        db.query(Loan)
        .options(joinedload(Loan.payments), joinedload(Loan.client))
        .join(Client)
        .filter(
            Loan.id == loan_id,
            Client.owner_id == user.get("id"),
        )
        .first()
    )

    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    if loan.is_completed:
        raise HTTPException(status_code=400, detail="Loan already completed")

    try:
        client = loan.client
        pending_payments = [p for p in loan.payments if not p.paid]

        if not pending_payments:
            raise HTTPException(status_code=400, detail="No pending payments")

        # Mark all pending as paid with today's date
        now = datetime.now()
        for payment in pending_payments:
            payment.paid = True
            payment.paid_at = now

        # Calculate and apply liquidation bonus
        bonus = calculate_liquidation_points(len(pending_payments, loan.amount))
        apply_points(client, bonus)

        db.commit()

        close_loan_if_completed(loan, db)

        return {
            "message": "Loan liquidated successfully",
            "payments_settled": len(pending_payments),
            "bonus_points": bonus,
            "total_points": client.loyalty_points,
        }

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error liquidating loan")