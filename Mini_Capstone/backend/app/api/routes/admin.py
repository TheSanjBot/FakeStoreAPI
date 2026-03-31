"""Admin routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.controllers.admin_controller import AdminController
from app.controllers.user_controller import UserController
from app.core.dependencies import get_admin_controller, get_user_controller, require_roles
from app.schemas.admin_schema import AdminReportResponse
from app.schemas.common import MessageResponse
from app.schemas.user_schema import UserListResponse
from app.utils.constants import Roles

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/reports", response_model=AdminReportResponse)
def reports(
    _: dict = Depends(require_roles(Roles.ADMIN)),
    controller: AdminController = Depends(get_admin_controller),
) -> dict:
    return controller.get_reports()


@router.get("/users", response_model=UserListResponse)
def list_users(
    _: dict = Depends(require_roles(Roles.ADMIN)),
    controller: UserController = Depends(get_user_controller),
) -> dict:
    return controller.list_users()


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: str,
    current_user: dict = Depends(require_roles(Roles.ADMIN)),
    controller: UserController = Depends(get_user_controller),
) -> dict:
    return controller.delete_user(user_id, current_user)
