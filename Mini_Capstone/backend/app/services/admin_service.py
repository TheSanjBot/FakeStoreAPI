"""Admin-specific orchestration."""

from __future__ import annotations

from app.repositories.hub_repository import HubRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.repositories.user_repository import UserRepository
from app.utils.constants import Roles, ShipmentStatus


class AdminService:
    def __init__(
        self,
        user_repository: UserRepository,
        shipment_repository: ShipmentRepository,
        hub_repository: HubRepository,
    ) -> None:
        self.user_repository = user_repository
        self.shipment_repository = shipment_repository
        self.hub_repository = hub_repository

    def get_reports(self) -> dict:
        return {
            "total_users": self.user_repository.count(),
            "total_customers": self.user_repository.count({"role": Roles.CUSTOMER}),
            "total_agents": self.user_repository.count({"role": Roles.AGENT}),
            "total_shipments": self.shipment_repository.count(),
            "shipments_by_status": {
                status: self.shipment_repository.count({"status": status}) for status in ShipmentStatus.ALL
            },
            "total_hubs": self.hub_repository.count(),
        }
