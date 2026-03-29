"""Shipment controller."""

from __future__ import annotations

from app.schemas.shipment_schema import ShipmentCreateRequest
from app.services.shipment_service import ShipmentService


class ShipmentController:
    def __init__(self, shipment_service: ShipmentService) -> None:
        self.shipment_service = shipment_service

    def create_shipment(self, payload: ShipmentCreateRequest, customer: dict) -> dict:
        return self.shipment_service.create_shipment(payload, customer)

    def list_shipments(self, current_user: dict) -> dict:
        return self.shipment_service.list_shipments(current_user)

    def delete_shipment(self, shipment_id: str, current_user: dict) -> dict:
        return self.shipment_service.delete_shipment(shipment_id, current_user)

    def assign_agent(self, shipment_id: str, agent_id: str) -> dict:
        return self.shipment_service.assign_agent(shipment_id, agent_id)
