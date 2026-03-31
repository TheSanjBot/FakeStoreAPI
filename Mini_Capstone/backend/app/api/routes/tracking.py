"""Tracking routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.controllers.tracking_controller import TrackingController
from app.core.dependencies import get_tracking_controller, require_roles
from app.schemas.tracking_schema import TrackingUpdateCreateRequest, TrackingUpdateResponse
from app.utils.constants import Roles

router = APIRouter(prefix="/tracking", tags=["Tracking"])


@router.post("/{shipment_id}", response_model=TrackingUpdateResponse, status_code=status.HTTP_201_CREATED)
def add_tracking_update(
    shipment_id: str,
    payload: TrackingUpdateCreateRequest,
    current_user: dict = Depends(require_roles(Roles.AGENT)),
    controller: TrackingController = Depends(get_tracking_controller),
) -> dict:
    return controller.add_tracking_update(shipment_id, payload, current_user)
