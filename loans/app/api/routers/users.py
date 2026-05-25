# 📦 Standard library

# 🌐 Third-party
from fastapi import APIRouter, HTTPException
from starlette import status

# 📁 Local imports
from ...db.models import User
from ...schemas.user import CreateUserRequest, UserResponse, UserProfileResponse
from ...core.security import hash_password
from ..deps import db_dependency, user_dependency

router = APIRouter(tags=["user"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(db: db_dependency, user_request: CreateUserRequest):
    existing_user = db.query(User).filter(User.email == user_request.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    create_user_model = User(
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=hash_password(user_request.password),
        is_active=True,
        role="user"
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return create_user_model

@router.get("/", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(user: user_dependency, db: db_dependency):
    return db.query(User).filter(User.id == user.get("id")).first()