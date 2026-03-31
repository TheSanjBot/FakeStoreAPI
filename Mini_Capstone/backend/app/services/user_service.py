"""User service layer."""

from __future__ import annotations

from app.core.config import get_settings
from app.core.database import get_database
from app.core.security import hash_password
from app.exceptions.custom_exceptions import ForbiddenException, NotFoundException
from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.utils.constants import Roles
from app.utils.helpers import serialize_mongo


class UserService:
    def __init__(self, user_repository: UserRepository | None = None) -> None:
        self.user_repository = user_repository or UserRepository(get_database())

    def list_users(self) -> dict:
        users = [self._sanitize_user(user) for user in self.user_repository.list_users()]
        return {"users": users}

    def list_agents(self) -> dict:
        users = [self._sanitize_user(user) for user in self.user_repository.list_users(Roles.AGENT)]
        return {"users": users}

    def delete_user(self, user_id: str, acting_user: dict) -> dict:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found.")
        if str(user["_id"]) == str(acting_user["_id"]):
            raise ForbiddenException("You cannot delete your own account.")
        deleted = self.user_repository.delete_by_id(user_id)
        if not deleted:
            raise NotFoundException("User not found.")
        return {"detail": "User deleted successfully."}

    def seed_admin_user(self) -> None:
        settings = get_settings()
        self._migrate_legacy_admin_email(settings.admin_seed_email)
        if self.user_repository.get_by_email(settings.admin_seed_email):
            return

        admin = UserModel(
            name=settings.admin_seed_name,
            email=settings.admin_seed_email,
            password=hash_password(settings.admin_seed_password),
            role=Roles.ADMIN,
        )
        self.user_repository.create(admin.to_document())

    def _migrate_legacy_admin_email(self, target_email: str) -> None:
        legacy_email = "admin@logistics.local"
        legacy_user = self.user_repository.get_by_email(legacy_email)
        if legacy_user is None:
            return

        current_user = self.user_repository.get_by_email(target_email)
        if current_user is None:
            self.user_repository.update_by_id(str(legacy_user["_id"]), {"email": target_email.lower()})
            return

        self.user_repository.delete_by_id(str(legacy_user["_id"]))

    @staticmethod
    def _sanitize_user(user: dict) -> dict:
        payload = serialize_mongo(user)
        payload.pop("password", None)
        return payload
