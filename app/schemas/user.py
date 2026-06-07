# 📦 Standard library
import re

# 🌐 Third-party
from pydantic import BaseModel, Field, EmailStr, field_validator


class CreateUserRequest(BaseModel):
    email: EmailStr
    first_name: str = Field(min_length=3, max_length=24, pattern="^[a-zA-Z ]+$")
    last_name: str = Field(min_length=3, max_length=24, pattern="^[a-zA-Z ]+$")
    password: str = Field(max_length=60)
    terms_accepted: bool

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[^\w\s]", value):
            raise ValueError("Password must contain at least one special character")

        return value

    @field_validator("terms_accepted")
    @classmethod
    def validate_terms(cls, value):

        if value is not True:
            raise ValueError("You must accept terms and conditions")

        return value

    model_config = {
        "json_schema": {
            "example": {
                "email": "email@email.com",
                "first_name": "Luis",
                "last_name": "Villa",
                "password": "Password@123",
                "terms_accepted": True
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
