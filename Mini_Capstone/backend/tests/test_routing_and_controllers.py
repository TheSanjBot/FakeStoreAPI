from __future__ import annotations

from unittest.mock import MagicMock

from app.api.router import api_router
from app.api.routes import admin as admin_routes
from app.api.routes import auth as auth_routes
from app.api.routes import hubs as hub_routes
from app.api.routes import shipments as shipment_routes
from app.api.routes import tracking as tracking_routes
from app.api.routes import users as user_routes
from app.controllers.admin_controller import AdminController
from app.controllers.auth_controller import AuthController
from app.controllers.hub_controller import HubController
from app.controllers.shipment_controller import ShipmentController
from app.controllers.tracking_controller import TrackingController
from app.controllers.user_controller import UserController
from app.schemas.auth_schema import LoginRequest
from app.schemas.hub_schema import HubCreateRequest, HubUpdateRequest
from app.schemas.shipment_schema import AssignAgentRequest, ShipmentCreateRequest
from app.schemas.tracking_schema import ShipmentStatusUpdateRequest, TrackingUpdateCreateRequest
from app.schemas.user_schema import RegisterRequest


def test_api_router_includes_expected_paths():
    paths = {route.path for route in api_router.routes}

    assert "/auth/register" in paths
    assert "/shipments" in paths
    assert "/shipments/{shipment_id}/assign-agent" in paths
    assert "/tracking/{shipment_id}" in paths
    assert "/users/agents" in paths
    assert "/admin/reports" in paths
    assert "/admin/hubs" in paths


def test_auth_routes_delegate_to_controller():
    controller = MagicMock()
    controller.register.return_value = {"id": "u1"}
    controller.login.return_value = {"access_token": "token"}
    controller.me.return_value = {"id": "u1", "role": "customer"}

    register_payload = RegisterRequest(
        name="Alice",
        email="alice@example.com",
        password="Password123",
        role="customer",
    )
    login_payload = LoginRequest(email="alice@example.com", password="Password123")
    current_user = {"id": "u1", "role": "customer"}

    assert auth_routes.register(register_payload, controller) == {"id": "u1"}
    assert auth_routes.login(login_payload, controller) == {"access_token": "token"}
    assert auth_routes.me(current_user, controller) == {"id": "u1", "role": "customer"}
    controller.register.assert_called_once_with(register_payload)
    controller.login.assert_called_once_with(login_payload)
    controller.me.assert_called_once_with(current_user)


def test_shipment_routes_delegate_to_controllers():
    shipment_controller = MagicMock()
    tracking_controller = MagicMock()
    shipment_controller.create_shipment.return_value = {"id": "s1"}
    shipment_controller.assign_agent.return_value = {"id": "s1", "assigned_agent": "a1"}
    tracking_controller.update_status.return_value = {"id": "s1", "status": "in_transit"}

    user = {"id": "u1", "role": "customer"}
    create_payload = ShipmentCreateRequest(source_address="Chennai", destination_address="Bangalore")
    assign_payload = AssignAgentRequest(agent_id="a1")
    status_payload = ShipmentStatusUpdateRequest(status="in_transit", location="Salem Hub", note="Arrived")

    assert shipment_routes.create_shipment(create_payload, user, shipment_controller) == {"id": "s1"}
    assert shipment_routes.assign_agent("s1", assign_payload, user, shipment_controller) == {
        "id": "s1",
        "assigned_agent": "a1",
    }
    assert shipment_routes.update_status("s1", status_payload, user, tracking_controller) == {
        "id": "s1",
        "status": "in_transit",
    }
    shipment_controller.create_shipment.assert_called_once_with(create_payload, user)
    shipment_controller.assign_agent.assert_called_once_with("s1", "a1")
    tracking_controller.update_status.assert_called_once_with("s1", status_payload, user)


def test_tracking_route_delegates_to_controller():
    controller = MagicMock()
    controller.add_tracking_update.return_value = {"id": "t1"}
    payload = TrackingUpdateCreateRequest(location="Hub 1", status="in_transit", note="Received")
    agent = {"id": "a1", "role": "agent"}

    assert tracking_routes.add_tracking_update("s1", payload, agent, controller) == {"id": "t1"}
    controller.add_tracking_update.assert_called_once_with("s1", payload, agent)


def test_user_admin_and_hub_routes_delegate():
    user_controller = MagicMock()
    admin_controller = MagicMock()
    hub_controller = MagicMock()
    user_controller.list_agents.return_value = {"users": []}
    user_controller.list_users.return_value = {"users": []}
    user_controller.delete_user.return_value = {"detail": "deleted"}
    admin_controller.get_reports.return_value = {"total_users": 3}
    hub_controller.create_hub.return_value = {"id": "h1"}
    hub_controller.update_hub.return_value = {"id": "h1", "city": "Madurai"}
    hub_controller.delete_hub.return_value = {"detail": "deleted"}

    actor = {"id": "admin1", "role": "admin"}
    create_payload = HubCreateRequest(hub_name="South Hub", city="Chennai")
    update_payload = HubUpdateRequest(city="Madurai")

    assert user_routes.list_agents(actor, user_controller) == {"users": []}
    assert admin_routes.reports(actor, admin_controller) == {"total_users": 3}
    assert admin_routes.list_users(actor, user_controller) == {"users": []}
    assert admin_routes.delete_user("u1", actor, user_controller) == {"detail": "deleted"}
    assert hub_routes.create_hub(create_payload, actor, hub_controller) == {"id": "h1"}
    assert hub_routes.update_hub("h1", update_payload, actor, hub_controller) == {"id": "h1", "city": "Madurai"}
    assert hub_routes.delete_hub("h1", actor, hub_controller) == {"detail": "deleted"}


def test_auth_controller_calls_service():
    service = MagicMock()
    controller = AuthController(service)
    register_payload = RegisterRequest(
        name="Alice",
        email="alice@example.com",
        password="Password123",
        role="customer",
    )
    login_payload = LoginRequest(email="alice@example.com", password="Password123")
    current_user = {"id": "u1"}

    controller.register(register_payload)
    controller.login(login_payload)
    controller.me(current_user)

    service.register.assert_called_once_with(register_payload)
    service.login.assert_called_once_with(login_payload)
    service.me.assert_called_once_with(current_user)


def test_shipment_controller_calls_service():
    service = MagicMock()
    controller = ShipmentController(service)
    payload = ShipmentCreateRequest(source_address="Chennai", destination_address="Bangalore")
    customer = {"id": "u1"}

    controller.create_shipment(payload, customer)
    controller.list_shipments(customer)
    controller.delete_shipment("s1", customer)
    controller.assign_agent("s1", "a1")

    service.create_shipment.assert_called_once_with(payload, customer)
    service.list_shipments.assert_called_once_with(customer)
    service.delete_shipment.assert_called_once_with("s1", customer)
    service.assign_agent.assert_called_once_with("s1", "a1")


def test_tracking_controller_calls_services():
    tracking_service = MagicMock()
    shipment_service = MagicMock()
    shipment = {"_id": "s1"}
    shipment_service.get_shipment_for_tracking.return_value = shipment
    tracking_service.build_tracking_timeline.return_value = {"tracking_number": "TRK1"}
    controller = TrackingController(tracking_service, shipment_service)
    payload = TrackingUpdateCreateRequest(location="Hub 1", status="in_transit", note="Done")
    status_payload = ShipmentStatusUpdateRequest(status="delivered", location="Doorstep", note="Delivered")
    agent = {"id": "a1"}
    current_user = {"id": "u1"}

    controller.add_tracking_update("s1", payload, agent)
    controller.update_status("s1", status_payload, agent)
    timeline = controller.track_shipment("TRK1", current_user)

    tracking_service.add_tracking_update.assert_called_once_with("s1", payload, agent)
    tracking_service.update_status.assert_called_once_with("s1", status_payload, agent)
    shipment_service.get_shipment_for_tracking.assert_called_once_with("TRK1")
    shipment_service.ensure_tracking_access.assert_called_once_with(shipment, current_user)
    tracking_service.build_tracking_timeline.assert_called_once_with(shipment)
    assert timeline == {"tracking_number": "TRK1"}


def test_user_admin_and_hub_controllers_call_services():
    user_service = MagicMock()
    admin_service = MagicMock()
    hub_service = MagicMock()

    user_controller = UserController(user_service)
    admin_controller = AdminController(admin_service)
    hub_controller = HubController(hub_service)

    create_payload = HubCreateRequest(hub_name="North Hub", city="Delhi")
    update_payload = HubUpdateRequest(city="Mumbai")
    actor = {"id": "admin1"}

    user_controller.list_users()
    user_controller.list_agents()
    user_controller.delete_user("u1", actor)
    admin_controller.get_reports()
    hub_controller.create_hub(create_payload)
    hub_controller.update_hub("h1", update_payload)
    hub_controller.delete_hub("h1")
    hub_controller.list_hubs()

    user_service.list_users.assert_called_once()
    user_service.list_agents.assert_called_once()
    user_service.delete_user.assert_called_once_with("u1", actor)
    admin_service.get_reports.assert_called_once()
    hub_service.create_hub.assert_called_once_with(create_payload)
    hub_service.update_hub.assert_called_once_with("h1", update_payload)
    hub_service.delete_hub.assert_called_once_with("h1")
    hub_service.list_hubs.assert_called_once()
