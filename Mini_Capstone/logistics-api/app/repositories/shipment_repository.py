"""Shipment repository."""

from __future__ import annotations

from pymongo import DESCENDING
from pymongo.database import Database

from app.repositories.base_repository import BaseRepository
from app.utils.helpers import to_object_id


class ShipmentRepository(BaseRepository):
    collection_name = "shipments"

    def __init__(self, database: Database) -> None:
        super().__init__(database)

    def create(self, document: dict) -> dict:
        document["customer_id"] = to_object_id(document["customer_id"])
        if document.get("assigned_agent"):
            document["assigned_agent"] = to_object_id(document["assigned_agent"])
        return self.insert_one(document)

    def get_by_tracking_number(self, tracking_number: str) -> dict | None:
        return self.collection.find_one({"tracking_number": tracking_number.upper()})

    def list_for_customer(self, customer_id: str) -> list[dict]:
        return list(
            self.collection.find({"customer_id": to_object_id(customer_id)}).sort("created_at", DESCENDING)
        )

    def list_for_agent(self, agent_id: str) -> list[dict]:
        return list(
            self.collection.find({"assigned_agent": to_object_id(agent_id)}).sort("created_at", DESCENDING)
        )
