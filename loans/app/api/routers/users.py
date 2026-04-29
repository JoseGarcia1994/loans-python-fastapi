# 📦 Standard library

# 🌐 Third-party
from fastapi import APIRouter
from starlette import status

# 📁 Local imports
from ...db.models import User
from ...schemas.user import CreateUserRequest, UserResponse
from ...core.security import hash_password
from ..deps import db_dependency

router = APIRouter()

@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(db: db_dependency, user_request: CreateUserRequest):
    create_user_model = User(
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=hash_password(user_request.password),
        is_active=True,
        role=user_request.role
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return create_user_model