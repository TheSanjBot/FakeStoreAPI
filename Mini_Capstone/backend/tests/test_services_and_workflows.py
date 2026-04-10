from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.exceptions.custom_exceptions import ForbiddenException
from app.schemas.auth_schema import LoginRequest
from app.schemas.hub_schema import HubCreateRequest, HubUpdateRequest
from app.schemas.shipment_schema import ShipmentCreateRequest
from app.schemas.tracking_schema import ShipmentStatusUpdateRequest, TrackingUpdateCreateRequest
from app.schemas.user_schema import RegisterRequest
from app.services import user_service as user_service_module
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.hub_service import HubService
from app.services.shipment_service import ShipmentService
from app.services.tracking_service import TrackingService
from app.services.user_service import UserService
from tests.fakes import FakeHubRepository, FakeShipmentRepository, FakeTrackingRepository, FakeUserRepository
from app.utils.constants import Roles


def test_auth_service_register_and_login_round_trip():
    user_repository = FakeUserRepository()
    service = AuthService(user_repository)
    register_payload = RegisterRequest(
        name="Alice",
        email="Alice@example.com",
        password="Password123",
        role="customer",
    )

    registered = service.register(register_payload)
    login = service.login(LoginRequest(email="alice@example.com", password="Password123"))

    assert registered["email"] == "alice@example.com"
    assert "password" not in registered
    assert login["token_type"] == "bearer"
    assert login["user"]["role"] == Roles.CUSTOMER


def test_auth_service_rejects_public_admin_registration():
    service = AuthService(FakeUserRepository())

    with pytest.raises(ForbiddenException):
        service.register(
            RegisterRequest(
                name="Boss",
                email="boss@example.com",
                password="Password123",
                role="admin",
            )
        )


def test_shipment_service_create_list_assign_and_delete(make_user, make_tracking):
    customer = make_user(role=Roles.CUSTOMER)
    agent = make_user(role=Roles.AGENT, email="agent@example.com")
    shipment_repository = FakeShipmentRepository()
    tracking_repository = FakeTrackingRepository()
    user_repository = FakeUserRepository([customer, agent])
    service = ShipmentService(shipment_repository, user_repository, tracking_repository)

    created = service.create_shipment(
        ShipmentCreateRequest(source_address="Chennai", destination_address="Bangalore"),
        customer,
    )
    created_id = created["id"]
    tracked = make_tracking(shipment_id=created_id, updated_by=agent["_id"])
    tracking_repository.create(tracked)

    customer_shipments = service.list_shipments(customer)
    assigned = service.assign_agent(created_id, str(agent["_id"]))

    assert created["tracking_number"].startswith("TRK")
    assert len(customer_shipments["shipments"]) == 1
    assert assigned["assigned_agent"] == str(agent["_id"])

    result = service.delete_shipment(created_id, customer)
    assert result == {"detail": "Shipment cancelled successfully."}


def test_shipment_service_tracking_access_checks(make_user, make_shipment):
    customer = make_user(role=Roles.CUSTOMER)
    other_user = make_user(role=Roles.CUSTOMER, email="other@example.com")
    agent = make_user(role=Roles.AGENT, email="agent@example.com")
    shipment = make_shipment(customer_id=customer["_id"], assigned_agent=agent["_id"])
    service = ShipmentService(FakeShipmentRepository([shipment]), FakeUserRepository([agent]), FakeTrackingRepository())

    service.ensure_tracking_access(shipment, customer)
    service.ensure_tracking_access(shipment, agent)

    with pytest.raises(ForbiddenException):
        service.ensure_tracking_access(shipment, other_user)


def test_tracking_service_updates_status_and_builds_timeline(make_user, make_shipment):
    customer = make_user(role=Roles.CUSTOMER)
    agent = make_user(role=Roles.AGENT)
    shipment = make_shipment(customer_id=customer["_id"], assigned_agent=agent["_id"])
    shipment_repository = FakeShipmentRepository([shipment])
    tracking_repository = FakeTrackingRepository()
    service = TrackingService(shipment_repository, tracking_repository)

    updated = service.update_status(
        str(shipment["_id"]),
        ShipmentStatusUpdateRequest(status="in_transit", location="Salem Hub", note="Scanned"),
        agent,
    )
    timeline = service.build_tracking_timeline(shipment_repository.get_by_id(str(shipment["_id"])))

    assert updated["status"] == "in_transit"
    assert timeline["current_status"] == "in_transit"
    assert len(timeline["updates"]) == 1


def test_tracking_service_rejects_wrong_agent(make_user, make_shipment):
    agent = make_user(role=Roles.AGENT)
    other_agent = make_user(role=Roles.AGENT, email="other-agent@example.com")
    shipment = make_shipment(assigned_agent=agent["_id"])
    service = TrackingService(FakeShipmentRepository([shipment]), FakeTrackingRepository())

    with pytest.raises(ForbiddenException):
        service.add_tracking_update(
            str(shipment["_id"]),
            TrackingUpdateCreateRequest(location="Hub 2", status="in_transit", note="Moved"),
            other_agent,
        )


def test_user_service_lists_agents_deletes_users_and_seeds_admin(monkeypatch, make_user):
    admin = make_user(role=Roles.ADMIN, email="admin@example.com")
    agent = make_user(role=Roles.AGENT, email="agent@example.com")
    customer = make_user(role=Roles.CUSTOMER, email="customer@example.com")
    repository = FakeUserRepository([admin, agent, customer])
    service = UserService(repository)

    agents = service.list_agents()
    deleted = service.delete_user(str(customer["_id"]), admin)

    monkeypatch.setattr(
        user_service_module,
        "get_settings",
        lambda: SimpleNamespace(
            admin_seed_name="Seed Admin",
            admin_seed_email="seed@example.com",
            admin_seed_password="Password123",
        ),
    )
    seed_repo = FakeUserRepository()
    UserService(seed_repo).seed_admin_user()

    assert len(agents["users"]) == 1
    assert deleted == {"detail": "User deleted successfully."}
    assert seed_repo.get_by_email("seed@example.com") is not None


def test_admin_service_and_hub_service_cover_reporting_and_hub_crud(make_user, make_shipment, make_hub):
    customer = make_user(role=Roles.CUSTOMER)
    agent = make_user(role=Roles.AGENT, email="agent@example.com")
    shipment = make_shipment(customer_id=customer["_id"], assigned_agent=agent["_id"], status="created")
    hub = make_hub(hub_name="Central Hub")

    admin_service = AdminService(
        FakeUserRepository([customer, agent]),
        FakeShipmentRepository([shipment]),
        FakeHubRepository([hub]),
    )
    hub_repository = FakeHubRepository()
    hub_service = HubService(hub_repository)

    report = admin_service.get_reports()
    created = hub_service.create_hub(HubCreateRequest(hub_name="South Hub", city="Chennai"))
    updated = hub_service.update_hub(str(created["id"]), HubUpdateRequest(city="Madurai"))
    listed = hub_service.list_hubs()
    deleted = hub_service.delete_hub(str(created["id"]))

    assert report["total_users"] == 2
    assert report["total_shipments"] == 1
    assert created["hub_name"] == "South Hub"
    assert updated["city"] == "Madurai"
    assert len(listed["hubs"]) == 1
    assert deleted == {"detail": "Hub deleted successfully."}
