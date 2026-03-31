"""Hub repository."""

from __future__ import annotations

from pymongo.database import Database

from app.repositories.base_repository import BaseRepository


class HubRepository(BaseRepository):
    collection_name = "hubs"

    def __init__(self, database: Database) -> None:
        super().__init__(database)

    def get_by_name(self, hub_name: str) -> dict | None:
        return self.collection.find_one({"hub_name": hub_name})
