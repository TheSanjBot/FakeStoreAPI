"""Shipment and agent routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.controllers.shipment_controller import ShipmentController
from app.controllers.tracking_controller import TrackingController
from app.core.dependencies import (
    get_shipment_controller,
    get_tracking_controller,
    require_roles,
)
from app.schemas.common import MessageResponse
from app.schemas.shipment_schema import AssignAgentRequest, ShipmentCreateRequest, ShipmentListResponse, ShipmentResponse
from app.schemas.tracking_schema import ShipmentStatusUpdateRequest, TrackingTimelineResponse
from app.utils.constants import Roles

router = APIRouter(tags=["Shipments"])


@router.post(
    "/shipments",
    response_model=ShipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_shipment(
    payload: ShipmentCreateRequest,
    current_user: dict = Depends(require_roles(Roles.CUSTOMER)),
    controller: ShipmentController = Depends(get_shipment_controller),
) -> dict:
    return controller.create_shipment(payload, current_user)


@router.get("/shipments", response_model=ShipmentListResponse)
def list_shipments(
    current_user: dict = Depends(require_roles(Roles.ADMIN, Roles.CUSTOMER, Roles.AGENT)),
    controller: ShipmentController = Depends(get_shipment_controller),
) -> dict:
    return controller.list_shipments(current_user)


@router.get("/shipments/{tracking_number}", response_model=TrackingTimelineResponse)
def track_shipment(
    tracking_number: str,
    current_user: dict = Depends(require_roles(Roles.ADMIN, Roles.CUSTOMER, Roles.AGENT)),
    controller: TrackingController = Depends(get_tracking_controller),
) -> dict:
    return controller.track_shipment(tracking_number, current_user)


@router.delete("/shipments/{shipment_id}", response_model=MessageResponse)
def cancel_shipment(
    shipment_id: str,
    current_user: dict = Depends(require_roles(Roles.CUSTOMER)),
    controller: ShipmentController = Depends(get_shipment_controller),
) -> dict:
    return controller.delete_shipment(shipment_id, current_user)


@router.put("/shipments/{shipment_id}/assign-agent", response_model=ShipmentResponse)
def assign_agent(
    shipment_id: str,
    payload: AssignAgentRequest,
    _: dict = Depends(require_roles(Roles.ADMIN)),
    controller: ShipmentController = Depends(get_shipment_controller),
) -> dict:
    return controller.assign_agent(shipment_id, payload.agent_id)


@router.put("/shipments/{shipment_id}/status", response_model=ShipmentResponse)
def update_status(
    shipment_id: str,
    payload: ShipmentStatusUpdateRequest,
    current_user: dict = Depends(require_roles(Roles.AGENT)),
    controller: TrackingController = Depends(get_tracking_controller),
) -> dict:
    return controller.update_status(shipment_id, payload, current_user)


@router.get("/agent/shipments", response_model=ShipmentListResponse)
def list_agent_shipments(
    current_user: dict = Depends(require_roles(Roles.AGENT)),
    controller: ShipmentController = Depends(get_shipment_controller),
) -> dict:
    return controller.list_shipments(current_user)
