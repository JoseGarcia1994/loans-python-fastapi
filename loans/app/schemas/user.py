# 📦 Standard library
from typing import Literal

# 🌐 Third-party
from pydantic import BaseModel, Field, EmailStr

class CreateUserRequest(BaseModel):
    email: EmailStr
    first_name: str = Field(min_length=3, max_length=24, pattern="^[a-zA-Z ]+$")
    last_name: str = Field(min_length=3, max_length=24, pattern="^[a-zA-Z ]+$")
    password: str = Field(min_length=8, max_length=60)
    role: Literal["admin", "user"]

    model_config = {
        "json_schema": {
            "example": {
                "email": "email@email.com",
                "first_name": "Jose",
                "last_name": "Garcia",
                "password": "password",
                "role": "user/admin",
            }
        }
    }

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    role: str