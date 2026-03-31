"""Tracking update domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.utils.helpers import utc_now


@dataclass(slots=True)
class TrackingUpdateModel:
    shipment_id: str
    location: str
    status: str
    updated_by: str
    note: str | None = None
    updated_at: datetime = field(default_factory=utc_now)

    def to_document(self) -> dict:
        return {
            "shipment_id": self.shipment_id,
            "location": self.location,
            "status": self.status,
            "updated_by": self.updated_by,
            "note": self.note,
            "updated_at": self.updated_at,
        }
