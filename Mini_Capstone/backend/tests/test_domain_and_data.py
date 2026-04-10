from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from bson import ObjectId
from pydantic import ValidationError

from app.exceptions.custom_exceptions import ValidationException
from app.models.hub_model import HubModel
from app.models.shipment_model import ShipmentModel
from app.models.tracking_model import TrackingUpdateModel
from app.models.user_model import UserModel
from app.repositories.base_repository import BaseRepository
from app.repositories.hub_repository import HubRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.repositories.tracking_repository import TrackingRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin_schema import AdminReportResponse
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.common import MessageResponse
from app.schemas.hub_schema import HubCreateRequest
from app.schemas.shipment_schema import ShipmentCreateRequest
from app.schemas.tracking_schema import TrackingUpdateCreateRequest
from app.schemas.user_schema import RegisterRequest, UserResponse
from app.utils.constants import Roles, ShipmentStatus, TRACKING_PREFIX
from app.utils.helpers import generate_tracking_number, serialize_mongo, to_object_id, utc_now


class ExampleRepository(BaseRepository):
    collection_name = "examples"


def test_user_model_serializes_lowercase_email():
    model = UserModel(name="Alice", email="ALICE@EXAMPLE.COM", password="hashed")
    document = model.to_document()

    assert document["email"] == "alice@example.com"
    assert document["role"] == "customer"


def test_shipment_model_to_document(make_user):
    customer = make_user()
    model = ShipmentModel(
        tracking_number="TRK1234",
        customer_id=str(customer["_id"]),
        source_address="Chennai",
        destination_address="Bangalore",
    )

    document = model.to_document()

    assert document["tracking_number"] == "TRK1234"
    assert document["status"] == "created"


def test_tracking_update_model_to_document(make_shipment, make_user):
    shipment = make_shipment()
    agent = make_user(role="agent")
    model = TrackingUpdateModel(
        shipment_id=str(shipment["_id"]),
        location="Salem Hub",
        status="in_transit",
        updated_by=str(agent["_id"]),
        note="Scanned",
    )

    document = model.to_document()

    assert document["location"] == "Salem Hub"
    assert document["status"] == "in_transit"


def test_hub_model_to_document():
    model = HubModel(hub_name="North Hub", city="Delhi")
    document = model.to_document()

    assert document["hub_name"] == "North Hub"
    assert document["city"] == "Delhi"


def test_base_repository_crud_helpers():
    collection = MagicMock()
    database = {"examples": collection}
    repo = ExampleRepository(database)
    inserted_id = ObjectId()
    created_doc = {"_id": inserted_id, "name": "created"}
    cursor = MagicMock()
    cursor.sort.return_value = ["sorted"]

    collection.insert_one.return_value.inserted_id = inserted_id
    collection.find_one.return_value = created_doc
    collection.find.return_value = cursor
    collection.find_one_and_update.return_value = {"updated": True}
    collection.delete_one.return_value.deleted_count = 1
    collection.count_documents.return_value = 3

    assert repo.insert_one({"name": "created"}) == created_doc
    assert repo.get_by_id(str(inserted_id)) == created_doc
    assert repo.list_all() == ["sorted"]
    assert repo.update_by_id(str(inserted_id), {"name": "updated"}) == {"updated": True}
    assert repo.delete_by_id(str(inserted_id)) is True
    assert repo.count() == 3


def test_user_repository_normalizes_email():
    repo = UserRepository({"users": MagicMock()})
    repo.insert_one = MagicMock(return_value={"email": "alice@example.com"})

    result = repo.create({"email": "ALICE@EXAMPLE.COM"})

    assert result == {"email": "alice@example.com"}
    assert repo.insert_one.call_args.args[0]["email"] == "alice@example.com"


def test_shipment_repository_converts_ids_before_insert():
    repo = ShipmentRepository({"shipments": MagicMock()})
    repo.insert_one = MagicMock(return_value={"ok": True})
    customer_id = str(ObjectId())
    agent_id = str(ObjectId())

    repo.create(
        {
            "tracking_number": "TRK1",
            "customer_id": customer_id,
            "assigned_agent": agent_id,
        }
    )

    payload = repo.insert_one.call_args.args[0]
    assert isinstance(payload["customer_id"], ObjectId)
    assert isinstance(payload["assigned_agent"], ObjectId)


def test_tracking_repository_converts_foreign_keys_before_insert():
    repo = TrackingRepository({"tracking_updates": MagicMock()})
    repo.insert_one = MagicMock(return_value={"ok": True})
    shipment_id = str(ObjectId())
    updated_by = str(ObjectId())

    repo.create(
        {
            "shipment_id": shipment_id,
            "updated_by": updated_by,
            "status": "in_transit",
            "location": "Hub 1",
        }
    )

    payload = repo.insert_one.call_args.args[0]
    assert isinstance(payload["shipment_id"], ObjectId)
    assert isinstance(payload["updated_by"], ObjectId)


def test_hub_repository_queries_by_name():
    collection = MagicMock()
    repo = HubRepository({"hubs": collection})

    repo.get_by_name("Central Hub")

    collection.find_one.assert_called_once_with({"hub_name": "Central Hub"})


def test_schema_models_accept_valid_payloads():
    now = datetime.now(timezone.utc)
    user = UserResponse(
        id="u1",
        name="Alice",
        email="alice@example.com",
        role="customer",
        is_active=True,
        created_at=now,
    )
    token = TokenResponse(access_token="token", user=user)
    report = AdminReportResponse(
        total_users=3,
        total_customers=1,
        total_agents=1,
        total_shipments=2,
        shipments_by_status={"created": 1},
        total_hubs=1,
    )
    message = MessageResponse(detail="ok")

    assert token.token_type == "bearer"
    assert report.total_users == 3
    assert message.detail == "ok"


def test_request_schemas_validate_invalid_input():
    with pytest.raises(ValidationError):
        RegisterRequest(name="A", email="bad@example.com", password="short", role="customer")

    with pytest.raises(ValidationError):
        LoginRequest(email="bad@example.com", password="short")

    with pytest.raises(ValidationError):
        ShipmentCreateRequest(source_address="A", destination_address="B")

    with pytest.raises(ValidationError):
        TrackingUpdateCreateRequest(location="A", status="created", note="x")

    with pytest.raises(ValidationError):
        HubCreateRequest(hub_name="A", city="B")


def test_utc_now_is_timezone_aware():
    assert utc_now().tzinfo is not None


def test_generate_tracking_number_uses_expected_prefix():
    tracking_number = generate_tracking_number()

    assert tracking_number.startswith(TRACKING_PREFIX)
    assert len(tracking_number) > len(TRACKING_PREFIX)


def test_to_object_id_validates_and_converts():
    object_id = ObjectId()

    assert to_object_id(str(object_id)) == object_id

    try:
        to_object_id("invalid-id")
    except ValidationException as exc:
        assert exc.detail == "Invalid object id supplied."
    else:
        raise AssertionError("Expected invalid object id to raise ValidationException")


def test_serialize_mongo_converts_nested_object_ids():
    nested_id = ObjectId()
    payload = {"_id": nested_id, "child": {"_id": nested_id}, "items": [nested_id]}
    serialized = serialize_mongo(payload)

    assert serialized["id"] == str(nested_id)
    assert serialized["child"]["id"] == str(nested_id)
    assert serialized["items"] == [str(nested_id)]


def test_constants_expose_roles_and_statuses():
    assert Roles.ADMIN in Roles.ALL
    assert ShipmentStatus.DELIVERED in ShipmentStatus.ALL
    assert ShipmentStatus.OUT_FOR_DELIVERY in ShipmentStatus.AGENT_ALLOWED
