# 📦 Standard library

# 🌐 Third-party
from typing import Annotated
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from starlette import status

# 📁 Local imports
from ..db.database import SessionLocal
from ..core.security import SECRET_KEY, ALGORITHM

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate credentials")
        return {"email": email, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")

user_dependency = Annotated[dict, Depends(get_current_user)]
