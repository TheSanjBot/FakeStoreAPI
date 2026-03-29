"""Auth controller."""

from __future__ import annotations

from app.schemas.auth_schema import LoginRequest
from app.schemas.user_schema import RegisterRequest
from app.services.auth_service import AuthService


class AuthController:
    def __init__(self, auth_service: AuthService) -> None:
        self.auth_service = auth_service

    def register(self, payload: RegisterRequest) -> dict:
        return self.auth_service.register(payload)

    def login(self, payload: LoginRequest) -> dict:
        return self.auth_service.login(payload)

    def me(self, current_user: dict) -> dict:
        return self.auth_service.me(current_user)
