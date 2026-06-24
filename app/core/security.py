# 📦 Standard library
import os
from datetime import datetime, timedelta, timezone

# 🌐 Third-party
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import jwt

load_dotenv()

# Hash password
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret and ALG will work togather to add a signature to the JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

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