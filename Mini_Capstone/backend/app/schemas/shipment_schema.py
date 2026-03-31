"""Shipment schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel


class ShipmentCreateRequest(APIModel):
    source_address: str = Field(min_length=2, max_length=200)
    destination_address: str = Field(min_length=2, max_length=200)


class AssignAgentRequest(APIModel):
    agent_id: str


class ShipmentResponse(APIModel):
    id: str
    tracking_number: str
    customer_id: str
    source_address: str
    destination_address: str
    status: str
    assigned_agent: str | None = None
    current_location: str | None = None
    created_at: datetime
    updated_at: datetime


class ShipmentListResponse(APIModel):
    shipments: list[ShipmentResponse]
