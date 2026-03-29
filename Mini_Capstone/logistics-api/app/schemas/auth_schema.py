"""Authentication schemas."""

from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.common import APIModel
from app.schemas.user_schema import UserResponse


class LoginRequest(APIModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
