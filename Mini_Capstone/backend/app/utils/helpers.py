"""Shared helper functions."""

from __future__ import annotations

from datetime import datetime, timezone
from secrets import token_hex
from typing import Any

from bson import ObjectId

from app.exceptions.custom_exceptions import ValidationException
from app.utils.constants import TRACKING_PREFIX


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_tracking_number() -> str:
    return f"{TRACKING_PREFIX}{token_hex(4).upper()}"


def to_object_id(value: str | ObjectId) -> ObjectId:
    if isinstance(value, ObjectId):
        return value
    if not ObjectId.is_valid(value):
        raise ValidationException("Invalid object id supplied.")
    return ObjectId(value)


def serialize_mongo(value: Any) -> Any:
    if isinstance(value, list):
        return [serialize_mongo(item) for item in value]
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        for key, item in value.items():
            output["id" if key == "_id" else key] = serialize_mongo(item)
        return output
    if isinstance(value, ObjectId):
        return str(value)
    return value
