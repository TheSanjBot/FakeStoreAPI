from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.security import HTTPAuthorizationCredentials
from httpx import ASGITransport, AsyncClient

from app import main as main_module
from app.core import config, dependencies, security
from app.core.database import get_database, mongo_database
from app.db.mongo_client import get_database as wrapped_get_database
from app.db.mongo_client import mongo_database as wrapped_mongo_database
from app.exceptions.custom_exceptions import ConflictException, ForbiddenException, UnauthorizedException, ValidationException
from app.exceptions.exception_handlers import register_exception_handlers
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.rate_limiter import SimpleRateLimiterMiddleware


async def get_response(app: FastAPI, path: str):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(path)


def test_get_settings_reads_environment(monkeypatch):
    config.get_settings.cache_clear()
    monkeypatch.setenv("APP_NAME", "Test Logistics API")

    settings = config.get_settings()

    assert settings.app_name == "Test Logistics API"
    config.get_settings.cache_clear()


def test_security_hash_verify_and_token_round_trip(monkeypatch):
    monkeypatch.setattr(security.settings, "jwt_secret", "test-secret")
    monkeypatch.setattr(security.settings, "jwt_algorithm", "HS256")

    hashed = security.hash_password("Password123")
    token = security.create_access_token(subject="user-1", role="admin", expires_minutes=5)
    payload = security.decode_access_token(token)

    assert security.verify_password("Password123", hashed) is True
    assert payload["sub"] == "user-1"
    assert payload["role"] == "admin"


def test_extract_bearer_token_requires_credentials():
    with pytest.raises(UnauthorizedException):
        security.extract_bearer_token(None)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="abc123")
    assert security.extract_bearer_token(credentials) == "abc123"


def test_require_roles_allows_matching_role_and_blocks_others():
    allow_admin = dependencies.require_roles("admin")

    assert allow_admin({"role": "admin"})["role"] == "admin"
    with pytest.raises(ForbiddenException):
        allow_admin({"role": "customer"})


def test_get_current_user_loads_active_user(monkeypatch, make_user):
    user = make_user(role="customer")

    monkeypatch.setattr(dependencies, "extract_bearer_token", lambda _: "token")
    monkeypatch.setattr(dependencies, "decode_access_token", lambda _: {"sub": str(user["_id"])})
    monkeypatch.setattr(
        dependencies,
        "get_user_repository",
        lambda: SimpleNamespace(get_by_id=lambda _: user),
    )

    current_user = dependencies.get_current_user(object())

    assert current_user["email"] == user["email"]


def test_get_current_user_rejects_inactive_user(monkeypatch, make_user):
    user = make_user(is_active=False)

    monkeypatch.setattr(dependencies, "extract_bearer_token", lambda _: "token")
    monkeypatch.setattr(dependencies, "decode_access_token", lambda _: {"sub": str(user["_id"])})
    monkeypatch.setattr(
        dependencies,
        "get_user_repository",
        lambda: SimpleNamespace(get_by_id=lambda _: user),
    )

    with pytest.raises(ForbiddenException):
        dependencies.get_current_user(object())


def test_db_wrapper_re_exports_database_helpers():
    assert wrapped_get_database is get_database
    assert wrapped_mongo_database is mongo_database


def test_custom_exceptions_keep_status_and_detail():
    exc = ConflictException("Duplicate resource")

    assert exc.status_code == 409
    assert exc.detail == "Duplicate resource"


def test_registered_exception_handler_returns_json():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom():
        raise ValidationException("Bad payload")

    response = asyncio.run(get_response(app, "/boom"))

    assert response.status_code == 422
    assert response.json() == {"detail": "Bad payload"}


def test_create_app_exposes_health_route(monkeypatch):
    class DummyUserService:
        def seed_admin_user(self) -> None:
            return None

    monkeypatch.setattr(main_module.mongo_database, "connect", lambda: None)
    monkeypatch.setattr(main_module.mongo_database, "ensure_indexes", lambda: None)
    monkeypatch.setattr(main_module.mongo_database, "close", lambda: None)
    monkeypatch.setattr(main_module, "UserService", DummyUserService)

    app = main_module.create_app()

    response = asyncio.run(get_response(app, "/health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_request_logging_middleware_logs_request(caplog):
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    caplog.set_level(logging.INFO, logger="logistics-api")

    response = asyncio.run(get_response(app, "/ping"))

    assert response.status_code == 200
    assert "GET /ping -> 200" in caplog.text


def test_rate_limiter_blocks_after_threshold():
    app = FastAPI()
    app.add_middleware(SimpleRateLimiterMiddleware, max_requests=1, window_seconds=60)

    @app.get("/ping")
    def ping():
        return {"ok": True}

    async def exercise_rate_limiter():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            first_response = await client.get("/ping")
            second_response = await client.get("/ping")
        return first_response, second_response

    first, second = asyncio.run(exercise_rate_limiter())

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json() == {"detail": "Rate limit exceeded."}
