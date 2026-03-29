"""Hub schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel


class HubCreateRequest(APIModel):
    hub_name: str = Field(min_length=2, max_length=100)
    city: str = Field(min_length=2, max_length=100)


class HubUpdateRequest(APIModel):
    hub_name: str | None = Field(default=None, min_length=2, max_length=100)
    city: str | None = Field(default=None, min_length=2, max_length=100)


class HubResponse(APIModel):
    id: str
    hub_name: str
    city: str
    created_at: datetime
    updated_at: datetime


class HubListResponse(APIModel):
    hubs: list[HubResponse]
