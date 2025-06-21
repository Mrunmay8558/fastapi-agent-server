from odmantic import Model, Field, ObjectId
from pydantic import EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
import re


class User(Model):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., unique=True, index=True)
    username: str = Field(..., min_length=3, max_length=50, unique=True, index=True)
    hashed_password: str = Field(...)
    phone: Optional[str] = Field(None)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    agent_ids: List[ObjectId] = Field(
        default_factory=list, description="List of agent IDs associated with this user"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None and not re.match(r"^\+?1?\d{9,15}$", v):
            raise ValueError("Invalid phone number format")
        return v

    model_config = {"collection": "users"}
