from __future__ import annotations

from copy import deepcopy
from typing import Any

from bson import ObjectId


def _normalize_id(value: str | ObjectId | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _matches(document: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    if not filters:
        return True
    for key, value in filters.items():
        if _normalize_id(document.get(key)) != _normalize_id(value):
            return False
    return True


def _to_object_id(value: str | ObjectId | None) -> str | ObjectId | None:
    if value is None or isinstance(value, ObjectId):
        return value
    return ObjectId(value)


class FakeUserRepository:
    def __init__(self, users: list[dict] | None = None) -> None:
        self.users = {str(user["_id"]): deepcopy(user) for user in users or []}

    def create(self, document: dict) -> dict:
        stored = deepcopy(document)
        stored.setdefault("_id", ObjectId())
        stored["email"] = stored["email"].lower()
        self.users[str(stored["_id"])] = stored
        return deepcopy(stored)

    def get_by_email(self, email: str) -> dict | None:
        email = email.lower()
        for user in self.users.values():
            if user["email"].lower() == email:
                return deepcopy(user)
        return None

    def get_by_id(self, user_id: str) -> dict | None:
        user = self.users.get(str(user_id))
        return deepcopy(user) if user else None

    def list_users(self, role: str | None = None) -> list[dict]:
        users = list(self.users.values())
        if role:
            users = [user for user in users if user["role"] == role]
        return deepcopy(users)

    def update_by_id(self, user_id: str, updates: dict) -> dict | None:
        user = self.users.get(str(user_id))
        if user is None:
            return None
        user.update(deepcopy(updates))
        if "email" in user:
            user["email"] = user["email"].lower()
        return deepcopy(user)

    def delete_by_id(self, user_id: str) -> bool:
        return self.users.pop(str(user_id), None) is not None

    def count(self, filters: dict | None = None) -> int:
        return sum(1 for user in self.users.values() if _matches(user, filters))


class FakeShipmentRepository:
    def __init__(self, shipments: list[dict] | None = None) -> None:
        self.shipments = {str(shipment["_id"]): deepcopy(shipment) for shipment in shipments or []}

    def create(self, document: dict) -> dict:
        stored = deepcopy(document)
        stored.setdefault("_id", ObjectId())
        stored["customer_id"] = _to_object_id(stored["customer_id"])
        if stored.get("assigned_agent"):
            stored["assigned_agent"] = _to_object_id(stored["assigned_agent"])
        self.shipments[str(stored["_id"])] = stored
        return deepcopy(stored)

    def get_by_id(self, shipment_id: str) -> dict | None:
        shipment = self.shipments.get(str(shipment_id))
        return deepcopy(shipment) if shipment else None

    def get_by_tracking_number(self, tracking_number: str) -> dict | None:
        for shipment in self.shipments.values():
            if shipment["tracking_number"] == tracking_number.upper():
                return deepcopy(shipment)
        return None

    def list_all(self, filters: dict | None = None) -> list[dict]:
        items = [shipment for shipment in self.shipments.values() if _matches(shipment, filters)]
        return deepcopy(items)

    def list_for_customer(self, customer_id: str) -> list[dict]:
        return deepcopy(
            [
                shipment
                for shipment in self.shipments.values()
                if _normalize_id(shipment["customer_id"]) == str(customer_id)
            ]
        )

    def list_for_agent(self, agent_id: str) -> list[dict]:
        return deepcopy(
            [
                shipment
                for shipment in self.shipments.values()
                if _normalize_id(shipment.get("assigned_agent")) == str(agent_id)
            ]
        )

    def update_by_id(self, shipment_id: str, updates: dict) -> dict | None:
        shipment = self.shipments.get(str(shipment_id))
        if shipment is None:
            return None
        shipment.update(deepcopy(updates))
        if shipment.get("assigned_agent"):
            shipment["assigned_agent"] = _to_object_id(shipment["assigned_agent"])
        return deepcopy(shipment)

    def delete_by_id(self, shipment_id: str) -> bool:
        return self.shipments.pop(str(shipment_id), None) is not None

    def count(self, filters: dict | None = None) -> int:
        return sum(1 for shipment in self.shipments.values() if _matches(shipment, filters))


class FakeTrackingRepository:
    def __init__(self, updates: list[dict] | None = None) -> None:
        self.updates = [deepcopy(update) for update in updates or []]

    def create(self, document: dict) -> dict:
        stored = deepcopy(document)
        stored.setdefault("_id", ObjectId())
        stored["shipment_id"] = _to_object_id(stored["shipment_id"])
        stored["updated_by"] = _to_object_id(stored["updated_by"])
        self.updates.append(stored)
        return deepcopy(stored)

    def list_by_shipment_id(self, shipment_id: str, newest_first: bool = False) -> list[dict]:
        items = [
            deepcopy(update)
            for update in self.updates
            if _normalize_id(update["shipment_id"]) == str(shipment_id)
        ]
        return sorted(items, key=lambda item: item["updated_at"], reverse=newest_first)

    def delete_for_shipment(self, shipment_id: str) -> int:
        before = len(self.updates)
        self.updates = [update for update in self.updates if _normalize_id(update["shipment_id"]) != str(shipment_id)]
        return before - len(self.updates)


class FakeHubRepository:
    def __init__(self, hubs: list[dict] | None = None) -> None:
        self.hubs = {str(hub["_id"]): deepcopy(hub) for hub in hubs or []}

    def insert_one(self, document: dict) -> dict:
        stored = deepcopy(document)
        stored.setdefault("_id", ObjectId())
        self.hubs[str(stored["_id"])] = stored
        return deepcopy(stored)

    def get_by_name(self, hub_name: str) -> dict | None:
        for hub in self.hubs.values():
            if hub["hub_name"] == hub_name:
                return deepcopy(hub)
        return None

    def update_by_id(self, hub_id: str, updates: dict) -> dict | None:
        hub = self.hubs.get(str(hub_id))
        if hub is None:
            return None
        hub.update(deepcopy(updates))
        return deepcopy(hub)

    def delete_by_id(self, hub_id: str) -> bool:
        return self.hubs.pop(str(hub_id), None) is not None

    def list_all(self) -> list[dict]:
        return deepcopy(list(self.hubs.values()))

    def count(self, filters: dict | None = None) -> int:
        return sum(1 for hub in self.hubs.values() if _matches(hub, filters))
