# 📦 Standard library

# 🌐 Third-party
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

# 📁 Local imports
from ..deps import db_dependency

router = APIRouter()

@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency
):
    return form_data.username