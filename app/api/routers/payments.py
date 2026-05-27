# 🌐 Third-party
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
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