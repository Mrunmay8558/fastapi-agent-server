from odmantic import Model, Field
from datetime import datetime
from typing import Optional


class BaseModel(Model):
    """Base model with common fields for all documents"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        pass  # Individual models will override collection names
