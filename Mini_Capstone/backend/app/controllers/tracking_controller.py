"""Tracking controller."""

from __future__ import annotations

from app.schemas.tracking_schema import ShipmentStatusUpdateRequest, TrackingUpdateCreateRequest
from app.services.shipment_service import ShipmentService
from app.services.tracking_service import TrackingService


class TrackingController:
    def __init__(self, tracking_service: TrackingService, shipment_service: ShipmentService) -> None:
        self.tracking_service = tracking_service
        self.shipment_service = shipment_service

    def add_tracking_update(self, shipment_id: str, payload: TrackingUpdateCreateRequest, agent: dict) -> dict:
        return self.tracking_service.add_tracking_update(shipment_id, payload, agent)

    def update_status(self, shipment_id: str, payload: ShipmentStatusUpdateRequest, agent: dict) -> dict:
        return self.tracking_service.update_status(shipment_id, payload, agent)

    def track_shipment(self, tracking_number: str, current_user: dict) -> dict:
        shipment = self.shipment_service.get_shipment_for_tracking(tracking_number)
        self.shipment_service.ensure_tracking_access(shipment, current_user)
        return self.tracking_service.build_tracking_timeline(shipment)
