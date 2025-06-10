from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models import ProviderConfig, AgentFeatures, PyObjectId


# User Schemas
class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    phone: Optional[str] = Field(None, regex=r"^\+?1?\d{9,15}$")


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = Field(None, regex=r"^\+?1?\d{9,15}$")


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    first_name: str
    last_name: str
    email: str
    username: str
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    agent_ids: List[str]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        allow_population_by_field_name = True


# Agent Schemas
class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    prompt: str = Field(..., description="System prompt for the agent")
    provider_config: ProviderConfig
    features: Optional[AgentFeatures] = Field(default_factory=AgentFeatures)


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    prompt: Optional[str] = None
    provider_config: Optional[ProviderConfig] = None
    features: Optional[AgentFeatures] = None
    is_active: Optional[bool] = None


class AgentResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: Optional[str]
    prompt: str
    provider_config: ProviderConfig
    features: AgentFeatures
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: str

    class Config:
        allow_population_by_field_name = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# Response Schemas
class MessageResponse(BaseModel):
    message: str
    status: str = "success"


class ErrorResponse(BaseModel):
    message: str
    status: str = "error"
    details: Optional[dict] = None