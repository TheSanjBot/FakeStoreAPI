"""Top-level API router."""

from fastapi import APIRouter

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.hubs import router as hubs_router
from app.api.routes.shipments import router as shipments_router
from app.api.routes.tracking import router as tracking_router
from app.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(shipments_router)
api_router.include_router(tracking_router)
api_router.include_router(hubs_router)
api_router.include_router(admin_router)
