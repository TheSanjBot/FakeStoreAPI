"""Shared repository helpers."""

from __future__ import annotations

from typing import Any

from pymongo import DESCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database

from app.exceptions.custom_exceptions import NotFoundException
from app.utils.helpers import to_object_id


class BaseRepository:
    collection_name: str

    def __init__(self, database: Database) -> None:
        self.collection: Collection = database[self.collection_name]

    def insert_one(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.collection.insert_one(document)
        created = self.collection.find_one({"_id": result.inserted_id})
        if created is None:
            raise NotFoundException("Created resource could not be loaded.")
        return created

    def get_by_id(self, entity_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"_id": to_object_id(entity_id)})

    def list_all(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return list(self.collection.find(filters or {}).sort("created_at", DESCENDING))

    def update_by_id(self, entity_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        if not updates:
            return self.get_by_id(entity_id)
        return self.collection.find_one_and_update(
            {"_id": to_object_id(entity_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )

    def delete_by_id(self, entity_id: str) -> bool:
        result = self.collection.delete_one({"_id": to_object_id(entity_id)})
        return result.deleted_count > 0

    def count(self, filters: dict[str, Any] | None = None) -> int:
        return self.collection.count_documents(filters or {})
