"""User domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.utils.constants import Roles
from app.utils.helpers import utc_now


@dataclass(slots=True)
class UserModel:
    name: str
    email: str
    password: str
    role: str = Roles.CUSTOMER
    is_active: bool = True
    created_at: datetime = field(default_factory=utc_now)

    def to_document(self) -> dict:
        return {
            "name": self.name,
            "email": self.email.lower(),
            "password": self.password,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }
