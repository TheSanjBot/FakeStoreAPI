"""Hub domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.utils.helpers import utc_now


@dataclass(slots=True)
class HubModel:
    hub_name: str
    city: str
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def to_document(self) -> dict:
        return {
            "hub_name": self.hub_name,
            "city": self.city,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
