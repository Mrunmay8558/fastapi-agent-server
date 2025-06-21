from odmantic import Model, Field, ObjectId, EmbeddedModel
from typing import Optional, List
from datetime import datetime


class ProviderConfig(EmbeddedModel):
    """Configuration for TTS, STT, and LLM providers"""

    tts_provider: str = Field(
        ..., description="Text-to-Speech provider (e.g., 'openai', 'elevenlabs')"
    )
    stt_provider: str = Field(
        ..., description="Speech-to-Text provider (e.g., 'openai', 'google')"
    )
    llm_provider: str = Field(
        ..., description="Large Language Model provider (e.g., 'openai', 'anthropic')"
    )

    # Provider-specific configurations
    tts_config: Optional[dict] = Field(default_factory=dict)
    stt_config: Optional[dict] = Field(default_factory=dict)
    llm_config: Optional[dict] = Field(default_factory=dict)


class AgentFeatures(EmbeddedModel):
    """Features enabled for the agent"""

    voice_chat: bool = Field(default=False)
    text_chat: bool = Field(default=True)
    file_upload: bool = Field(default=False)
    web_search: bool = Field(default=False)
    memory: bool = Field(default=True)
    custom_functions: List[str] = Field(default_factory=list)


class Agent(Model):
    name: str = Field(..., min_length=1, max_length=100, index=True)
    description: Optional[str] = Field(None, max_length=500)
    prompt: str = Field(..., description="System prompt for the agent")
    provider_config: ProviderConfig
    features: AgentFeatures = Field(default_factory=AgentFeatures)
    is_active: bool = Field(default=True)
    created_by: ObjectId = Field(..., description="User ID who created this agent", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"collection": "agents"}
