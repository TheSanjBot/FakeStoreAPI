"""Tracking repository."""

from __future__ import annotations

from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database

from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class TrackingRepository(BaseRepository):
    collection_name = "tracking_updates"

    def __init__(self, database: Database) -> None:
        super().__init__(database)

    def create(self, document: dict) -> dict:
        document["shipment_id"] = to_object_id(document["shipment_id"])
        document["updated_by"] = to_object_id(document["updated_by"])
        return self.insert_one(document)

    def list_by_shipment_id(self, shipment_id: str, newest_first: bool = False) -> list[dict]:
        direction = DESCENDING if newest_first else ASCENDING
        return list(
            self.collection.find({"shipment_id": to_object_id(shipment_id)}).sort("updated_at", direction)
        )

    def delete_for_shipment(self, shipment_id: str) -> int:
        result = self.collection.delete_many({"shipment_id": to_object_id(shipment_id)})
        return result.deleted_count
