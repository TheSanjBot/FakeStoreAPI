from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from bson import ObjectId

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def now() -> datetime:
    return datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def make_user(now):
    def factory(
        *,
        name: str = "User One",
        email: str = "user@example.com",
        password: str = "hashed-password",
        role: str = "customer",
        is_active: bool = True,
        user_id: ObjectId | None = None,
    ) -> dict:
        return {
            "_id": user_id or ObjectId(),
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "is_active": is_active,
            "created_at": now,
        }

    return factory


@pytest.fixture
def make_shipment(now):
    def factory(
        *,
        tracking_number: str = "TRK12345678",
        customer_id: ObjectId | None = None,
        status: str = "created",
        assigned_agent: ObjectId | None = None,
        current_location: str | None = None,
        shipment_id: ObjectId | None = None,
    ) -> dict:
        return {
            "_id": shipment_id or ObjectId(),
            "tracking_number": tracking_number,
            "customer_id": customer_id or ObjectId(),
            "source_address": "Chennai",
            "destination_address": "Bangalore",
            "status": status,
            "assigned_agent": assigned_agent,
            "current_location": current_location,
            "created_at": now,
            "updated_at": now,
        }

    return factory


@pytest.fixture
def make_tracking(now):
    def factory(
        *,
        shipment_id: ObjectId | None = None,
        updated_by: ObjectId | None = None,
        status: str = "in_transit",
        location: str = "Salem Hub",
        note: str | None = "Checked in",
        tracking_id: ObjectId | None = None,
    ) -> dict:
        return {
            "_id": tracking_id or ObjectId(),
            "shipment_id": shipment_id or ObjectId(),
            "location": location,
            "status": status,
            "updated_by": updated_by or ObjectId(),
            "note": note,
            "updated_at": now,
        }

    return factory


@pytest.fixture
def make_hub(now):
    def factory(
        *,
        hub_name: str = "Central Hub",
        city: str = "Chennai",
        hub_id: ObjectId | None = None,
    ) -> dict:
        return {
            "_id": hub_id or ObjectId(),
            "hub_name": hub_name,
            "city": city,
            "created_at": now,
            "updated_at": now,
        }

    return factory
