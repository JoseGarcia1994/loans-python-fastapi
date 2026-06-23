# 📦 Standard library
from datetime import date, timedelta, datetime

# 🌐 Third-party
from fastapi import Path, HTTPException, Query, APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from starlette import status

# 📁 Local imports
from ..deps import db_dependency, user_dependency
from ...db.models import Loan, Payment, Client
from ...schemas.loan import LoanRequest, UpdateLoanRequest
from ...services.loan_service import generate_payment_schedule, get_monday

router = APIRouter(tags=["loan"])

@router.get("/", status_code=status.HTTP_200_OK)
async def get_loans(
    user: user_dependency,
    db: db_dependency,
):

    return (
        db.query(Loan)
        .options(
            joinedload(Loan.payments),
            joinedload(Loan.client),
        )
        .join(Client)
        .filter(
            Client.owner_id == user.get("id")
        )
        .all()
    )

@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_dashboard_stats(user: user_dependency, db: db_dependency):

    loans = (
        db.query(Loan)
        .options(
            joinedload(Loan.payments),
            joinedload(Loan.client),
        )
        .join(Client)
        .filter(
            Client.owner_id == user.get("id")
        )
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

@router.get("/by-date", status_code=status.HTTP_200_OK)
async def get_loan_by_date(
        user: user_dependency,
        db: db_dependency,
        date: date = Query(..., description="Date in format YYYY-MM-DD"),
):
    loans = (
        db.query(Loan)
        .options(
            joinedload(Loan.payments),
            joinedload(Loan.client),
        )
        .join(Client)
        .filter(
            Loan.start_date == date,
            Client.owner_id == user.get("id"),
        )
        .all()
    )

    if not loans:
        raise HTTPException(status_code=404, detail="No loans found for this date")
    return loans

@router.get("/{loan_id}", status_code=status.HTTP_200_OK)
async def get_loan_by_id(
        user: user_dependency,
        db: db_dependency,
        loan_id: int = Path(gt=0),
):
    loan = (
        db.query(Loan)
        .options(
            joinedload(Loan.payments),
            joinedload(Loan.client),
        )
        .join(Client)
        .filter(
            Loan.id == loan_id,
            Client.owner_id == user.get("id"),
        )
        .first()
    )

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    return loan

@router.post("/", status_code=201)
async def create_loan(
    user: user_dependency,
    db: db_dependency,
    loan_request: LoanRequest
):
    try:
        # 📌 Validate client
        client = (
            db.query(Client)
            .filter(
                Client.id == loan_request.client_id,
                Client.owner_id == user.get("id"),
            )
            .first()
        )

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # 🚨 NEW RULE: only 1 active loan
        active_loan = (
            db.query(Loan)
            .filter(
                Loan.client_id == loan_request.client_id,
                Loan.is_completed == False,
            )
            .first()
        )

        if active_loan:
            raise HTTPException(
                status_code=400,
                detail="Client already has an active loan"
            )

        # 📌 Change to Monday
        start_date = get_monday(loan_request.start_date)

        # 📌 Create Loan
        new_loan = Loan(
            client_id=loan_request.client_id,
            amount=loan_request.amount,
            start_date=start_date,
            end_date=start_date + timedelta(weeks=14),
            total_weeks=14,
            status="active",
        )

        db.add(new_loan)
        db.commit()
        db.refresh(new_loan)

        # 📌 Generate weekly payments
        payment_dates = generate_payment_schedule(start_date)

        payment_amount = int(loan_request.amount * 0.10)

        for i, payment_date in enumerate(payment_dates):
            payment = Payment(
                payment_number=i + 1,
                payment_amount=payment_amount,
                payment_date=payment_date,
                paid=False,
                loan_id=new_loan.id,
            )
            db.add(payment)

        db.commit()

        return new_loan

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating loan")

@router.put("/{loan_id}", response_model=LoanRequest | None, status_code=status.HTTP_200_OK)
async def update_loan(
        user: user_dependency,
        db: db_dependency,
        loan: UpdateLoanRequest,
        loan_id: int = Path(gt=0)
):
    loan_model = (
        db.query(Loan)
        .join(Client)
        .filter(
            Loan.id == loan_id,
            Client.owner_id == user.get("id"),
        )
        .first()
    )

    if loan_model is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    update_data = loan.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(loan_model, key, value)

    db.commit()
    db.refresh(loan_model)

    # Find next monday
    payment_dates = generate_payment_schedule(loan.start_date)

    payments = db.query(Payment).filter(Payment.loan_id == loan_model.id).all()

    payment_amount = int(
        loan.amount * 0.10
    )

    for i, payment in enumerate(payments):
        payment.payment_date = payment_dates[i]
        payment.payment_amount = payment_amount

    db.commit()

    return loan_model

@router.patch(
    "/{loan_id}/complete",
    status_code=status.HTTP_200_OK,
)
async def complete_loan(
    user: user_dependency,
    db: db_dependency,
    loan_id: int = Path(gt=0),
):

    loan = (
        db.query(Loan)
        .options(
            joinedload(Loan.payments),
            joinedload(Loan.client),
        )
        .join(Client)
        .filter(
            Loan.id == loan_id,
            Client.owner_id == user.get("id"),
        )
        .first()
    )

    if not loan:
        raise HTTPException(
            status_code=404,
            detail="Loan not found",
        )

    if loan.is_completed:
        raise HTTPException(
            status_code=400,
            detail="Loan already completed",
        )

    try:

        pending_payments = [
            payment
            for payment in loan.payments
            if not payment.paid
        ]

        for payment in pending_payments:
            payment.paid = True
            payment.paid_at = datetime.now()

        loan.is_completed = True
        loan.completed_at = datetime.now()
        loan.status = "completed"

        weeks_used = (
            (loan.completed_at.date() - loan.start_date).days // 7
        ) + 1

        bonus_points = 0

        if weeks_used <= 10:
            bonus_points = 50

        elif weeks_used <= 13:
            bonus_points = 20

        loan.client.loyalty_points += bonus_points

        db.commit()

        return {
            "message": "Loan completed successfully",
            "bonus_points": bonus_points,
            "weeks_used": weeks_used,
            "remaining_payments_paid": len(pending_payments),
            "total_points": loan.client.loyalty_points,
        }

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error completing loan",
        )


@router.delete("/{loan_id}",  status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(user: user_dependency, db: db_dependency, loan_id: int = Path(gt=0)):
    loan = (
        db.query(Loan)
        .join(Client)
        .filter(
            Loan.id == loan_id,
            Client.owner_id == user.get("id"),
        )
        .first()
    )

    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    try:
        db.delete(loan)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting loan")