"""Admin controller."""

from __future__ import annotations

from app.services.admin_service import AdminService


class AdminController:
    def __init__(self, admin_service: AdminService) -> None:
        self.admin_service = admin_service

    def get_reports(self) -> dict:
        return self.admin_service.get_reports()
