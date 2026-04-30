# 📁 Local imports
from ..core.security import bcrypt_context
from ..db.models import User

def authenticate_user(email: str, password: str, db):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user