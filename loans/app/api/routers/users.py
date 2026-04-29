# 📦 Standard library

# 🌐 Third-party
from fastapi import APIRouter

# 📁 Local imports
from ...db.models import User
from ...schemas.user import CreateUserRequest
from ...core.security import hash_password

router = APIRouter()

@router.post("/users")
async def create_user(user_request: CreateUserRequest):
    create_user_model = User(
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=hash_password(user_request.password),
        is_active=True,
        role=user_request.role
    )

    return create_user_model