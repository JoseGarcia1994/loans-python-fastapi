# 📦 Standard library
from datetime import datetime
from typing import Optional

# 🌐 Third-party
from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    first_name: str
    last_name: str
    phone: str

    address: Optional[str] = None

    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    first_name: Optional[str] = None

    last_name: Optional[str] = None

    phone: Optional[str] = None

    address: Optional[str] = None

    notes: Optional[str] = None

    is_active: Optional[bool] = None


class ClientResponse(ClientBase):
    id: int

    loyalty_points: int

    reward_level: str

    is_active: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )