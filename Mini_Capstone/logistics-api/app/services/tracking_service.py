"""Tracking service layer."""

from __future__ import annotations

from app.exceptions.custom_exceptions import ForbiddenException, NotFoundException, ValidationException
from app.models.tracking_model import TrackingUpdateModel
from app.repositories.shipment_repository import ShipmentRepository
from app.repositories.tracking_repository import TrackingRepository
from app.schemas.tracking_schema import ShipmentStatusUpdateRequest, TrackingUpdateCreateRequest
from app.utils.constants import Roles, ShipmentStatus
from app.utils.helpers import serialize_mongo, utc_now


class TrackingService:
    def __init__(
        self,
        shipment_repository: ShipmentRepository,
        tracking_repository: TrackingRepository,
    ) -> None:
        self.shipment_repository = shipment_repository
        self.tracking_repository = tracking_repository

    def add_tracking_update(self, shipment_id: str, payload: TrackingUpdateCreateRequest, agent: dict) -> dict:
        shipment = self._validate_agent_access(shipment_id, agent)
        self._validate_status(payload.status)

        tracking_update = TrackingUpdateModel(
            shipment_id=str(shipment["_id"]),
            location=payload.location,
            status=payload.status,
            updated_by=str(agent["_id"]),
            note=payload.note,
        )
        created = self.tracking_repository.create(tracking_update.to_document())
        self.shipment_repository.update_by_id(
            shipment_id,
            {
                "status": payload.status,
                "current_location": payload.location,
                "updated_at": utc_now(),
            },
        )
        return serialize_mongo(created)

    def update_status(self, shipment_id: str, payload: ShipmentStatusUpdateRequest, agent: dict) -> dict:
        shipment = self._validate_agent_access(shipment_id, agent)
        self._validate_status(payload.status)

        self.tracking_repository.create(
            TrackingUpdateModel(
                shipment_id=str(shipment["_id"]),
                location=payload.location,
                status=payload.status,
                updated_by=str(agent["_id"]),
                note=payload.note,
            ).to_document()
        )
        updated = self.shipment_repository.update_by_id(
            shipment_id,
            {
                "status": payload.status,
                "current_location": payload.location,
                "updated_at": utc_now(),
            },
        )
        if updated is None:
            raise NotFoundException("Shipment not found.")
        return serialize_mongo(updated)

    def build_tracking_timeline(self, shipment: dict) -> dict:
        updates = self.tracking_repository.list_by_shipment_id(str(shipment["_id"]))
        return {
            "tracking_number": shipment["tracking_number"],
            "shipment_id": str(shipment["_id"]),
            "current_status": shipment["status"],
            "current_location": shipment.get("current_location"),
            "updates": [serialize_mongo(item) for item in updates],
        }

    def _validate_agent_access(self, shipment_id: str, agent: dict) -> dict:
        shipment = self.shipment_repository.get_by_id(shipment_id)
        if shipment is None:
            raise NotFoundException("Shipment not found.")
        if agent["role"] != Roles.AGENT:
            raise ForbiddenException("Only agents can update shipment tracking.")
        if str(shipment.get("assigned_agent")) != str(agent["_id"]):
            raise ForbiddenException("This shipment is not assigned to the current agent.")
        return shipment

    @staticmethod
    def _validate_status(status: str) -> None:
        if status not in ShipmentStatus.AGENT_ALLOWED:
            raise ValidationException("Agents can only set in_transit, out_for_delivery, or delivered.")
