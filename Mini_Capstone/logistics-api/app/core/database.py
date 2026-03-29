"""MongoDB connection management."""

from __future__ import annotations

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from pymongo.server_api import ServerApi

from app.core.config import get_settings


class MongoDatabase:
    def __init__(self) -> None:
        self._client: MongoClient | None = None
        self._database: Database | None = None

    def connect(self) -> Database:
        if self._database is None:
            settings = get_settings()
            self._client = MongoClient(settings.mongo_uri, server_api=ServerApi("1"))
            # Ping eagerly so Atlas misconfiguration fails during startup.
            self._client.admin.command("ping")
            self._database = self._client[settings.mongo_db]
        return self._database

    def get_database(self) -> Database:
        return self.connect()

    def ensure_indexes(self) -> None:
        database = self.get_database()
        database["users"].create_index([("email", ASCENDING)], unique=True)
        database["shipments"].create_index([("tracking_number", ASCENDING)], unique=True)
        database["shipments"].create_index([("customer_id", ASCENDING)])
        database["shipments"].create_index([("assigned_agent", ASCENDING)])
        database["tracking_updates"].create_index([("shipment_id", ASCENDING)])
        database["hubs"].create_index([("hub_name", ASCENDING)], unique=True)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
        self._client = None
        self._database = None


mongo_database = MongoDatabase()


def get_database() -> Database:
    return mongo_database.get_database()
