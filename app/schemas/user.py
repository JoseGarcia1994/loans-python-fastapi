# 📦 Standard library
import re

# 🌐 Third-party
from pydantic import BaseModel, Field, EmailStr, field_validator


class CreateUserRequest(BaseModel):
    email: EmailStr
    first_name: str = Field(min_length=3, max_length=24, pattern="^[a-zA-Z ]+$")
    last_name: str = Field(min_length=3, max_length=24, pattern="^[a-zA-Z ]+$")
    password: str = Field(max_length=60)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[^\w\s]", value):
            raise ValueError("Password must contain at least one special character")

        return value

    model_config = {
        "json_schema": {
            "example": {
                "email": "email@email.com",
                "first_name": "Jose",
                "last_name": "Garcia",
                "password": "Password@123"
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

class UserProfileResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str

    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=6,)
