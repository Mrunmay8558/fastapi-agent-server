from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from odmantic import ObjectId


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, pattern=r"^\+?1?\d{9,15}$")


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# Properties to return via API
class User(UserBase):
    id: ObjectId = Field(alias="_id")
    agent_ids: List[ObjectId] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class UserInDB(User):
    hashed_password: str


# Enhanced response schemas with populated agents
class UserWithAgents(BaseModel):
    """User response with populated agent models"""

    id: ObjectId = Field(alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    phone: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    agent_ids: List[ObjectId] = Field(default_factory=list)
    agents: List[dict] = Field(
        default_factory=list, description="Populated agent models"
    )
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class UserAgentSummary(BaseModel):
    """Lightweight user response with agent count"""

    id: ObjectId = Field(alias="_id")
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    is_active: bool
    agent_count: int = Field(description="Number of agents owned by this user")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
