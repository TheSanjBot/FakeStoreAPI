"""User routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.controllers.user_controller import UserController
from app.core.dependencies import get_user_controller, require_roles
from app.schemas.user_schema import UserListResponse
from app.utils.constants import Roles

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/agents", response_model=UserListResponse)
def list_agents(
    _: dict = Depends(require_roles(Roles.ADMIN)),
    controller: UserController = Depends(get_user_controller),
) -> dict:
    return controller.list_agents()
