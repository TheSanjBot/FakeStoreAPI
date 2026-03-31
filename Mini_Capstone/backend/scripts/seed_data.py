"""Populate the database with a few starter records."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.core.database import mongo_database
from app.core.security import hash_password
from app.models.hub_model import HubModel
from app.models.user_model import UserModel
from app.repositories.hub_repository import HubRepository
from app.repositories.user_repository import UserRepository
from app.utils.constants import Roles


def seed() -> None:
    mongo_database.connect()
    mongo_database.ensure_indexes()

    database = mongo_database.get_database()
    user_repository = UserRepository(database)
    hub_repository = HubRepository(database)

    users = [
        UserModel(
            name="Sample Customer",
            email="customer@example.com",
            password=hash_password("Customer@123"),
            role=Roles.CUSTOMER,
        ),
        UserModel(
            name="Sample Agent",
            email="agent@example.com",
            password=hash_password("Agent@123"),
            role=Roles.AGENT,
        ),
    ]

    for user in users:
        if not user_repository.get_by_email(user.email):
            user_repository.create(user.to_document())

    hubs = [
        HubModel(hub_name="Salem Hub", city="Salem"),
        HubModel(hub_name="Bangalore Hub", city="Bangalore"),
    ]

    for hub in hubs:
        if not hub_repository.get_by_name(hub.hub_name):
            hub_repository.insert_one(hub.to_document())

    mongo_database.close()
    print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed()
