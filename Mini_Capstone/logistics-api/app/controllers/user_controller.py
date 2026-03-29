"""User controller."""

from __future__ import annotations

from app.services.user_service import UserService


class UserController:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    def list_users(self) -> dict:
        return self.user_service.list_users()

    def list_agents(self) -> dict:
        return self.user_service.list_agents()

    def delete_user(self, user_id: str, acting_user: dict) -> dict:
        return self.user_service.delete_user(user_id, acting_user)
