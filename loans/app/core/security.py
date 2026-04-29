# 🌐 Third-party
from passlib.context import CryptContext

# Hash password
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)
