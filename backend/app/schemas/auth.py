from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(examples=["ada@example.com"])
    password: str = Field(min_length=12, max_length=128, examples=["correct-horse-battery-staple"])


class LoginRequest(BaseModel):
    email: EmailStr = Field(examples=["ada@example.com"])
    password: str = Field(min_length=1, max_length=128, examples=["correct-horse-battery-staple"])


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
