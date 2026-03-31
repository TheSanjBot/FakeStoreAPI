"""Hub controller."""

from __future__ import annotations

from app.schemas.hub_schema import HubCreateRequest, HubUpdateRequest
from app.services.hub_service import HubService


class HubController:
    def __init__(self, hub_service: HubService) -> None:
        self.hub_service = hub_service

    def create_hub(self, payload: HubCreateRequest) -> dict:
        return self.hub_service.create_hub(payload)

    def update_hub(self, hub_id: str, payload: HubUpdateRequest) -> dict:
        return self.hub_service.update_hub(hub_id, payload)

    def delete_hub(self, hub_id: str) -> dict:
        return self.hub_service.delete_hub(hub_id)

    def list_hubs(self) -> dict:
        return self.hub_service.list_hubs()
