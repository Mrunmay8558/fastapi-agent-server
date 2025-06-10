from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ProviderConfig(BaseModel):
    """Configuration for TTS, STT, and LLM providers"""
    tts_provider: str = Field(..., description="Text-to-Speech provider (e.g., 'openai', 'elevenlabs')")
    stt_provider: str = Field(..., description="Speech-to-Text provider (e.g., 'openai', 'google')")
    llm_provider: str = Field(..., description="Large Language Model provider (e.g., 'openai', 'anthropic')")
    
    # Provider-specific configurations
    tts_config: Optional[dict] = Field(default_factory=dict)
    stt_config: Optional[dict] = Field(default_factory=dict)
    llm_config: Optional[dict] = Field(default_factory=dict)


class AgentFeatures(BaseModel):
    """Features enabled for the agent"""
    voice_chat: bool = Field(default=False, description="Enable voice chat capability")
    text_chat: bool = Field(default=True, description="Enable text chat capability")
    file_upload: bool = Field(default=False, description="Enable file upload capability")
    web_search: bool = Field(default=False, description="Enable web search capability")
    memory: bool = Field(default=True, description="Enable conversation memory")
    custom_functions: List[str] = Field(default_factory=list, description="List of custom function names")


class Agent(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    prompt: str = Field(..., description="System prompt for the agent")
    provider_config: ProviderConfig
    features: AgentFeatures = Field(default_factory=AgentFeatures)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: PyObjectId = Field(..., description="User ID who created this agent")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., unique=True)
    username: str = Field(..., min_length=3, max_length=50, unique=True)
    hashed_password: str = Field(...)
    phone: Optional[str] = Field(None, regex=r"^\+?1?\d{9,15}$")
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    agent_ids: List[PyObjectId] = Field(default_factory=list, description="List of agent IDs associated with this user")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}