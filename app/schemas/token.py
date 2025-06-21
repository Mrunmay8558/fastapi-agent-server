from pydantic import BaseModel
from typing import Optional


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None


# Message schemas
class Msg(BaseModel):
    msg: str


# Login schema
class UserLogin(BaseModel):
    username: str
    password: str


# Login response
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict  # Will contain user data
