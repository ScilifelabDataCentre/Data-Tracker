"""Tests for dataset requests."""
# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import

import helpers
import structure
import utils


def test_available_schema_list():
    """Get a list of the available schemas."""
    responses = helpers.make_request_all_roles("/api/v1/schema", ret_json=True)
    for response in responses:
        assert response.code == 200
        assert response.data["schemas"] == ["collection", "dataset", "order", "user"]


def test_schema_collection():
    """Confirm the schema of a collection."""
    responses = helpers.make_request_all_roles(
        "/api/v1/schema/collection", ret_json=True
    )
    expected = structure.collection()
    utils.prepare_response(expected)
    expected["id"] = ""
    for response in responses:
        assert response.code == 200
        assert response.data["collection"] == expected


def test_schema_dataset():
    """Confirm the schema of a dataset."""
    responses = helpers.make_request_all_roles("/api/v1/schema/dataset", ret_json=True)
    expected = structure.dataset()
    utils.prepare_response(expected)
    expected["id"] = ""
    for response in responses:
        assert response.code == 200
        assert response.data["dataset"] == expected


def test_schema_order():
    """Confirm the schema of a order."""
    responses = helpers.make_request_all_roles("/api/v1/schema/order", ret_json=True)
    expected = structure.order()
    utils.prepare_response(expected)
    expected["id"] = ""
    for response in responses:
        assert response.code == 200
        assert response.data["order"] == expected


def test_schema_user():
    """Confirm the schema of a user."""
    responses = helpers.make_request_all_roles("/api/v1/schema/user", ret_json=True)
    expected = structure.user()
    utils.prepare_response(expected)
    expected["id"] = ""
    for response in responses:
        assert response.code == 200
        assert response.data["user"] == expected
