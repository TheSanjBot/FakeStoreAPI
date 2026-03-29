"""Authentication business logic."""

from __future__ import annotations

from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions.custom_exceptions import ConflictException, ForbiddenException, UnauthorizedException
from app.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequest
from app.schemas.user_schema import RegisterRequest
from app.utils.constants import Roles
from app.utils.helpers import serialize_mongo


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def register(self, payload: RegisterRequest) -> dict:
        role = payload.role.lower()
        if role not in {Roles.CUSTOMER, Roles.AGENT}:
            raise ForbiddenException("Public registration is limited to customer and agent roles.")

        if self.user_repository.get_by_email(str(payload.email)):
            raise ConflictException("A user with this email already exists.")

        user = UserModel(
            name=payload.name,
            email=str(payload.email),
            password=hash_password(payload.password),
            role=role,
        )
        created = self.user_repository.create(user.to_document())
        return self._sanitize_user(created)

    def login(self, payload: LoginRequest) -> dict:
        user = self.user_repository.get_by_email(str(payload.email))
        if user is None or not verify_password(payload.password, user["password"]):
            raise UnauthorizedException("Invalid email or password.")
        if not user.get("is_active", True):
            raise ForbiddenException("This user has been deactivated.")

        token = create_access_token(subject=str(user["_id"]), role=user["role"])
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": self._sanitize_user(user),
        }

    def me(self, current_user: dict) -> dict:
        return self._sanitize_user(current_user)

    @staticmethod
    def _sanitize_user(user: dict) -> dict:
        payload = serialize_mongo(user)
        payload.pop("password", None)
        return payload
