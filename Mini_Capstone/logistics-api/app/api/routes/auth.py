"""Authentication routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.controllers.auth_controller import AuthController
from app.core.dependencies import get_auth_controller, get_current_user
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.user_schema import RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    controller: AuthController = Depends(get_auth_controller),
) -> dict:
    return controller.register(payload)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    controller: AuthController = Depends(get_auth_controller),
) -> dict:
    return controller.login(payload)


@router.get("/me", response_model=UserResponse)
def me(
    current_user: dict = Depends(get_current_user),
    controller: AuthController = Depends(get_auth_controller),
) -> dict:
    return controller.me(current_user)
