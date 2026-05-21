# 📦 Standard library

# 🌐 Third-party
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import joinedload
from starlette import status

# 📁 Local imports
from ..deps import db_dependency, user_dependency
from ...db.models import Loan

router = APIRouter(
    tags=["admin"],
)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_loans(user: user_dependency, db: db_dependency):
    if user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorized"
        )

    return db.query(Loan).options(joinedload(Loan.payments)).all()