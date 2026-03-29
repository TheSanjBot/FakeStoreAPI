"""Dependency providers and RBAC helpers."""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.controllers.admin_controller import AdminController
from app.controllers.auth_controller import AuthController
from app.controllers.hub_controller import HubController
from app.controllers.shipment_controller import ShipmentController
from app.controllers.tracking_controller import TrackingController
from app.controllers.user_controller import UserController
from app.core.database import get_database
from app.core.security import bearer_scheme, decode_access_token, extract_bearer_token
from app.exceptions.custom_exceptions import ForbiddenException, UnauthorizedException
from app.repositories.hub_repository import HubRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.repositories.tracking_repository import TrackingRepository
from app.repositories.user_repository import UserRepository
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.hub_service import HubService
from app.services.shipment_service import ShipmentService
from app.services.tracking_service import TrackingService
from app.services.user_service import UserService


def get_user_repository() -> UserRepository:
    return UserRepository(get_database())


def get_shipment_repository() -> ShipmentRepository:
    return ShipmentRepository(get_database())


def get_tracking_repository() -> TrackingRepository:
    return TrackingRepository(get_database())


def get_hub_repository() -> HubRepository:
    return HubRepository(get_database())


def get_auth_service() -> AuthService:
    return AuthService(get_user_repository())


def get_user_service() -> UserService:
    return UserService(get_user_repository())


def get_shipment_service() -> ShipmentService:
    return ShipmentService(get_shipment_repository(), get_user_repository(), get_tracking_repository())


def get_tracking_service() -> TrackingService:
    return TrackingService(get_shipment_repository(), get_tracking_repository())


def get_hub_service() -> HubService:
    return HubService(get_hub_repository())


def get_admin_service() -> AdminService:
    return AdminService(get_user_repository(), get_shipment_repository(), get_hub_repository())


def get_auth_controller() -> AuthController:
    return AuthController(get_auth_service())


def get_user_controller() -> UserController:
    return UserController(get_user_service())


def get_shipment_controller() -> ShipmentController:
    return ShipmentController(get_shipment_service())


def get_tracking_controller() -> TrackingController:
    return TrackingController(get_tracking_service(), get_shipment_service())


def get_hub_controller() -> HubController:
    return HubController(get_hub_service())


def get_admin_controller() -> AdminController:
    return AdminController(get_admin_service())


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    token = extract_bearer_token(credentials)
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token payload is invalid.")

    user = get_user_repository().get_by_id(user_id)
    if user is None:
        raise UnauthorizedException("User associated with the token was not found.")
    if not user.get("is_active", True):
        raise ForbiddenException("This account has been deactivated.")
    return user


def require_roles(*roles: str):
    def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in roles:
            raise ForbiddenException("You do not have permission to access this route.")
        return current_user

    return dependency
