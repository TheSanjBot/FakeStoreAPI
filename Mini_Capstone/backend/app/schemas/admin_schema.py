"""Admin reporting schemas."""

from __future__ import annotations

from app.schemas.common import APIModel


class AdminReportResponse(APIModel):
    total_users: int
    total_customers: int
    total_agents: int
    total_shipments: int
    shipments_by_status: dict[str, int]
    total_hubs: int
