# 📦 Standard library
import os
import secrets
from datetime import datetime, timedelta, timezone

# 🌐 Third-party
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt, JWTError

load_dotenv()

# Hash password
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret and ALG will work togather to add a signature to the JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30")
)

def create_password_reset_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "purpose": "password_reset",
        "jti": secrets.token_urlsafe(16),
        "iat": datetime.now(timezone.utc),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_password_reset_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("purpose") != "password_reset":
            return None

        user_id = payload.get("sub")

        if not user_id:
            return None

        return int(user_id)

    except (JWTError, ValueError, TypeError):
        return None

def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)

def create_access_token(
    email: str,
    user_id: int,
    role: str,
    expires_delta: timedelta,
):
    encode = {
        "sub": email,
        "id": user_id,
        "role": role,
    }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)