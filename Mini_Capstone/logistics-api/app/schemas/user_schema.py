"""User-facing schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.common import APIModel
from app.utils.constants import Roles


class UserResponse(APIModel):
    id: str
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime


class RegisterRequest(APIModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = Roles.CUSTOMER


class UserListResponse(APIModel):
    users: list[UserResponse]
