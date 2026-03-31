"""Hub management routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.controllers.hub_controller import HubController
from app.core.dependencies import get_hub_controller, require_roles
from app.schemas.common import MessageResponse
from app.schemas.hub_schema import HubCreateRequest, HubListResponse, HubResponse, HubUpdateRequest
from app.utils.constants import Roles

router = APIRouter(prefix="/admin/hubs", tags=["Hubs"])


@router.post("", response_model=HubResponse, status_code=status.HTTP_201_CREATED)
def create_hub(
    payload: HubCreateRequest,
    _: dict = Depends(require_roles(Roles.ADMIN)),
    controller: HubController = Depends(get_hub_controller),
) -> dict:
    return controller.create_hub(payload)


@router.get("", response_model=HubListResponse)
def list_hubs(
    _: dict = Depends(require_roles(Roles.ADMIN)),
    controller: HubController = Depends(get_hub_controller),
) -> dict:
    return controller.list_hubs()


@router.put("/{hub_id}", response_model=HubResponse)
def update_hub(
    hub_id: str,
    payload: HubUpdateRequest,
    _: dict = Depends(require_roles(Roles.ADMIN)),
    controller: HubController = Depends(get_hub_controller),
) -> dict:
    return controller.update_hub(hub_id, payload)


@router.delete("/{hub_id}", response_model=MessageResponse)
def delete_hub(
    hub_id: str,
    _: dict = Depends(require_roles(Roles.ADMIN)),
    controller: HubController = Depends(get_hub_controller),
) -> dict:
    return controller.delete_hub(hub_id)
