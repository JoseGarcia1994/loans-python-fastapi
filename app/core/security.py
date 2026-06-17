# 📦 Standard library
from datetime import datetime, timedelta, timezone

# 🌐 Third-party
from passlib.context import CryptContext
from jose import jwt

# Hash password
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)

# Secret and ALG will work togather to add a signature to the JWT
SECRET_KEY = "InGodWeTrust"
ALGORITHM = "HS256"

def create_access_token(
    email: str,
    user_id: int,
    role: str,
    first_name: str,
    last_name: str,
    expires_delta: timedelta,
):
    encode = {
        "sub": email,
        "id": user_id,
        "role": role,
        "first_name": first_name,
        "last_name": last_name,
    }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)