"""Tracking schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel


class TrackingUpdateCreateRequest(APIModel):
    location: str = Field(min_length=2, max_length=200)
    status: str
    note: str | None = Field(default=None, max_length=500)


class ShipmentStatusUpdateRequest(APIModel):
    status: str
    location: str = Field(min_length=2, max_length=200)
    note: str | None = Field(default=None, max_length=500)


class TrackingUpdateResponse(APIModel):
    id: str
    shipment_id: str
    location: str
    status: str
    updated_by: str
    note: str | None = None
    updated_at: datetime


class TrackingTimelineResponse(APIModel):
    tracking_number: str
    shipment_id: str
    current_status: str
    current_location: str | None = None
    updates: list[TrackingUpdateResponse]
