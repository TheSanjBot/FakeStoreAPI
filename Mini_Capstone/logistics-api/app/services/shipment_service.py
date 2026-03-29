"""Shipment service layer."""

from __future__ import annotations

from app.exceptions.custom_exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.shipment_model import ShipmentModel
from app.repositories.shipment_repository import ShipmentRepository
from app.repositories.tracking_repository import TrackingRepository
from app.repositories.user_repository import UserRepository
from app.schemas.shipment_schema import ShipmentCreateRequest
from app.utils.constants import Roles, ShipmentStatus
from app.utils.helpers import generate_tracking_number, serialize_mongo, utc_now


class ShipmentService:
    def __init__(
        self,
        shipment_repository: ShipmentRepository,
        user_repository: UserRepository,
        tracking_repository: TrackingRepository,
    ) -> None:
        self.shipment_repository = shipment_repository
        self.user_repository = user_repository
        self.tracking_repository = tracking_repository

    def create_shipment(self, payload: ShipmentCreateRequest, customer: dict) -> dict:
        shipment = ShipmentModel(
            tracking_number=generate_tracking_number(),
            customer_id=str(customer["_id"]),
            source_address=payload.source_address,
            destination_address=payload.destination_address,
        )
        created = self.shipment_repository.create(shipment.to_document())
        return serialize_mongo(created)

    def list_shipments(self, current_user: dict) -> dict:
        role = current_user["role"]
        if role == Roles.ADMIN:
            shipments = self.shipment_repository.list_all()
        elif role == Roles.CUSTOMER:
            shipments = self.shipment_repository.list_for_customer(str(current_user["_id"]))
        else:
            shipments = self.shipment_repository.list_for_agent(str(current_user["_id"]))
        return {"shipments": [serialize_mongo(item) for item in shipments]}

    def delete_shipment(self, shipment_id: str, current_user: dict) -> dict:
        shipment = self.shipment_repository.get_by_id(shipment_id)
        if shipment is None:
            raise NotFoundException("Shipment not found.")
        if str(shipment["customer_id"]) != str(current_user["_id"]):
            raise ForbiddenException("You can only cancel your own shipments.")
        if shipment["status"] != ShipmentStatus.CREATED:
            raise ConflictException("Only newly created shipments can be cancelled.")

        self.tracking_repository.delete_for_shipment(shipment_id)
        self.shipment_repository.delete_by_id(shipment_id)
        return {"detail": "Shipment cancelled successfully."}

    def assign_agent(self, shipment_id: str, agent_id: str) -> dict:
        shipment = self.shipment_repository.get_by_id(shipment_id)
        if shipment is None:
            raise NotFoundException("Shipment not found.")

        agent = self.user_repository.get_by_id(agent_id)
        if agent is None or agent["role"] != Roles.AGENT:
            raise NotFoundException("Agent not found.")

        updated = self.shipment_repository.update_by_id(
            shipment_id,
            {"assigned_agent": agent["_id"], "updated_at": utc_now()},
        )
        if updated is None:
            raise NotFoundException("Shipment not found.")
        return serialize_mongo(updated)

    def get_shipment_for_tracking(self, tracking_number: str) -> dict:
        shipment = self.shipment_repository.get_by_tracking_number(tracking_number)
        if shipment is None:
            raise NotFoundException("Shipment not found.")
        return shipment

    def ensure_tracking_access(self, shipment: dict, current_user: dict) -> None:
        if current_user["role"] == Roles.ADMIN:
            return
        if current_user["role"] == Roles.CUSTOMER and str(shipment["customer_id"]) == str(current_user["_id"]):
            return
        if current_user["role"] == Roles.AGENT and str(shipment.get("assigned_agent")) == str(current_user["_id"]):
            return
        raise ForbiddenException("You do not have access to this shipment.")
