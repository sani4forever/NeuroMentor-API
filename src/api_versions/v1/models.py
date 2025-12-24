"""
Pydantic models for API version 1.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Error(BaseModel):
    error: str

class UserCreateRequest(BaseModel):
    model_config = {'extra': 'ignore'}

    name: str = Field(..., description="First name of the user")
    gender: Optional[str] = Field(None, description="Gender of the user")
    age: Optional[int] = Field(None, description="Age of the user")

class UserResponse(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    telegram_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: int
    session_id: int
    message: str

class AIResponse(BaseModel):
    answer: str
    session_id: int

class Error(BaseModel):
    error: str