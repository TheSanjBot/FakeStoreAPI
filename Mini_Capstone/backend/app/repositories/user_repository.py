"""User repository."""

from __future__ import annotations

from pymongo.database import Database

from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    collection_name = "users"

    def __init__(self, database: Database) -> None:
        super().__init__(database)

    def create(self, document: dict) -> dict:
        document["email"] = document["email"].lower()
        return self.insert_one(document)

    def get_by_email(self, email: str) -> dict | None:
        return self.collection.find_one({"email": email.lower()})

    def list_users(self, role: str | None = None) -> list[dict]:
        filters = {"role": role} if role else None
        return self.list_all(filters)
