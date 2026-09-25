# 📦 Standard library
from datetime import datetime

# 🌐 Third-party
from fastapi import APIRouter, HTTPException, BackgroundTasks
from starlette import status

# 📁 Local imports
from ...db.models import User
from ...schemas.user import (
    ChangePasswordRequest,
    CreateUserRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserProfileResponse,
    UserResponse,
)
from ...core.security import (
    bcrypt_context,
    create_password_reset_token,
    hash_password,
    verify_password_reset_token,
)
from ...services.email_service import (
    send_password_reset_email,
    send_welcome_email,
)
from ..deps import db_dependency, user_dependency

router = APIRouter(tags=["user"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(db: db_dependency, user_request: CreateUserRequest, background_tasks: BackgroundTasks):
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
        role="user",

        terms_accepted = user_request.terms_accepted,
        terms_accepted_at = datetime.now() if user_request.terms_accepted else None,
        terms_version = "v1"
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    # 📧 Sends the email in the background, without blocking the response
    background_tasks.add_task(
        send_welcome_email,
        create_user_model.email,
        create_user_model.first_name,
    )

    return create_user_model

@router.get(
    "/",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK
)
async def get_current_user_profile(
    user: user_dependency,
    db: db_dependency
):
    user_model = (
        db.query(User)
        .filter(
            User.id == user.get("id")
        )
        .first()
    )

    if user_model is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user_model

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, password_request: ChangePasswordRequest):
    user_model = db.query(User).filter(User.id == user.get("id")).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt_context.verify(password_request.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect current password")

    if password_request.password == password_request.new_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different"
        )

    user_model.hashed_password = hash_password(
        password_request.new_password
    )

    db.commit()

@router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: db_dependency,
    background_tasks: BackgroundTasks,
):
    user_model = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    # No revelar si el correo está registrado.
    if user_model:
        reset_token = create_password_reset_token(
            user_id=user_model.id
        )

        background_tasks.add_task(
            send_password_reset_email,
            user_model.email,
            user_model.first_name,
            reset_token,
        )

    return {
        "message": "If the email exists, recovery instructions will be sent"
    }


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reset_password(
    request: ResetPasswordRequest,
    db: db_dependency,
):
    user_id = verify_password_reset_token(request.token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired recovery link",
        )

    user_model = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired recovery link",
        )

    if bcrypt_context.verify(
        request.new_password,
        user_model.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different",
        )

    user_model.hashed_password = hash_password(
        request.new_password
    )

    db.commit()
