# 📦 Standard library

# 🌐 Third-party
from fastapi import APIRouter, HTTPException, Path
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from starlette import status

# 📁 Local imports
from ..deps import db_dependency, user_dependency
from ...db.models import Loan, User
from ...schemas.user import UserResponse

router = APIRouter(
    tags=["admin"],
)

@router.get("/loans", status_code=status.HTTP_200_OK)
async def get_loans(user: user_dependency, db: db_dependency):
    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    return db.query(Loan).options(joinedload(Loan.payments)).all()

@router.get("/users",  response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_users(user: user_dependency, db: db_dependency):
    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )
    return db.query(User).all()

@router.delete("loans/{loan_id}",  status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(user: user_dependency, db: db_dependency, loan_id: int = Path(gt=0)):
    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )
    loan = db.query(Loan).filter(Loan.id == loan_id).first()

    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    try:
        db.delete(loan)
        db.commit()

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting loan")