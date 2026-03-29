"""Shipment domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.utils.constants import ShipmentStatus
from app.utils.helpers import utc_now


@dataclass(slots=True)
class ShipmentModel:
    tracking_number: str
    customer_id: str
    source_address: str
    destination_address: str
    status: str = ShipmentStatus.CREATED
    assigned_agent: str | None = None
    current_location: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def to_document(self) -> dict:
        return {
            "tracking_number": self.tracking_number,
            "customer_id": self.customer_id,
            "source_address": self.source_address,
            "destination_address": self.destination_address,
            "status": self.status,
            "assigned_agent": self.assigned_agent,
            "current_location": self.current_location,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
