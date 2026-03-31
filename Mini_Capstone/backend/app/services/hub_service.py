"""Hub service layer."""

from __future__ import annotations

from app.exceptions.custom_exceptions import ConflictException, NotFoundException
from app.models.hub_model import HubModel
from app.repositories.hub_repository import HubRepository
from app.schemas.hub_schema import HubCreateRequest, HubUpdateRequest
from app.utils.helpers import serialize_mongo, utc_now


class HubService:
    def __init__(self, hub_repository: HubRepository) -> None:
        self.hub_repository = hub_repository

    def create_hub(self, payload: HubCreateRequest) -> dict:
        if self.hub_repository.get_by_name(payload.hub_name):
            raise ConflictException("A hub with this name already exists.")

        hub = HubModel(hub_name=payload.hub_name, city=payload.city)
        created = self.hub_repository.insert_one(hub.to_document())
        return serialize_mongo(created)

    def update_hub(self, hub_id: str, payload: HubUpdateRequest) -> dict:
        updates = payload.model_dump(exclude_none=True)
        updates["updated_at"] = utc_now()
        updated = self.hub_repository.update_by_id(hub_id, updates)
        if updated is None:
            raise NotFoundException("Hub not found.")
        return serialize_mongo(updated)

    def delete_hub(self, hub_id: str) -> dict:
        if not self.hub_repository.delete_by_id(hub_id):
            raise NotFoundException("Hub not found.")
        return {"detail": "Hub deleted successfully."}

    def list_hubs(self) -> dict:
        hubs = [serialize_mongo(hub) for hub in self.hub_repository.list_all()]
        return {"hubs": hubs}
