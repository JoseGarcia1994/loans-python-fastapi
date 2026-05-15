# 📦 Standard library
from datetime import timedelta
from typing import Annotated

# 🌐 Third-party
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

# 📁 Local imports
from ..deps import db_dependency
from ...services.auth_service import authenticate_user
from ...schemas.auth_schema import Token
from ...core.security import create_access_token

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(user.email, user.id, timedelta(minutes=20))

    return {
        "access_token": token,
        "token_type": "bearer",
    }