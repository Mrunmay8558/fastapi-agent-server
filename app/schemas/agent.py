from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from odmantic import ObjectId


# Standard Pydantic models for API schemas (not ODMantic embedded models)
class ProviderConfig(BaseModel):
    """Configuration for TTS, STT, and LLM providers"""
    tts_provider: str = Field(..., description="Text-to-Speech provider")
    stt_provider: str = Field(..., description="Speech-to-Text provider")
    llm_provider: str = Field(..., description="Large Language Model provider")
    tts_config: Optional[dict] = Field(default_factory=dict)
    stt_config: Optional[dict] = Field(default_factory=dict)
    llm_config: Optional[dict] = Field(default_factory=dict)


class AgentFeatures(BaseModel):
    """Features enabled for the agent"""
    voice_chat: bool = Field(default=False)
    text_chat: bool = Field(default=True)
    file_upload: bool = Field(default=False)
    web_search: bool = Field(default=False)
    memory: bool = Field(default=True)
    custom_functions: List[str] = Field(default_factory=list)


# Shared properties
class AgentBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    provider_config: Optional[ProviderConfig] = None
    features: Optional[AgentFeatures] = None
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class AgentCreate(AgentBase):
    name: str = Field(..., min_length=1, max_length=100)
    prompt: str = Field(..., description="System prompt for the agent")
    provider_config: ProviderConfig
    features: Optional[AgentFeatures] = Field(default_factory=AgentFeatures)


# Properties to receive via API on update
class AgentUpdate(AgentBase):
    pass


# Properties to return via API
class Agent(AgentBase):
    id: ObjectId = Field(alias="_id")
    name: str
    prompt: str
    provider_config: ProviderConfig
    features: AgentFeatures
    created_by: ObjectId
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class AgentInDB(Agent):
    pass