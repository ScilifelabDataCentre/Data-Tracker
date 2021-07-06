"""Tests for dataset requests."""
import itertools
import uuid
import requests

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import
import helpers
from helpers import (
    as_user,
    dataset_for_tests,
    TEST_LABEL,
    mdb,
    add_dataset,
    delete_fixture_dataset,
)


def test_list_datasets(mdb):
    """
    Confirm that listing datasets work as intended.

    Tests:

      * Confirm all datasets in the database are listed.
      * Confirm that the correct fields are included
    """
    responses = helpers.make_request_all_roles("/api/v1/dataset", ret_json=True)
    expected_fields = {"title", "id", "tags", "properties"}
    for response in responses:
        assert response.code == 200
        assert len(response.data["datasets"]) == mdb["datasets"].count_documents({})
        assert set(response.data["datasets"][0].keys()) == expected_fields


def test_list_user_datasets_permissions():
    """
    Confirm that users get the correct status code response.

    Tests:

      * Confirm that non-logged in users get 401, logged in users 200
    """
    responses = helpers.make_request_all_roles("/api/v1/dataset/user")
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 200


def test_list_user_datasets_with_datasets(mdb):
    """
    Confirm that users get the correct datasets.

    Tests:

      * Select a few users, confirm that the returned datasets are correct
      * Confirm that the included fields are the intended ones
    """
    session = requests.Session()
    orders = mdb["orders"].aggregate(
        [{"$match": {"datasets": {"$not": {"$size": 0}}}}, {"$sample": {"size": 2}}]
    )
    user_uuids = list(itertools.chain.from_iterable(order["editors"] for order in orders))
    users = mdb["users"].find({"_id": {"$in": list(user_uuids)}})
    for user in users:
        user_orders = list(mdb["orders"].find({"editors": user["_id"]}, {"datasets": 1}))
        user_datasets = list(
            itertools.chain.from_iterable(order["datasets"] for order in user_orders)
        )
        user_datasets = [str(uuid) for uuid in user_datasets]

        helpers.as_user(session, user["auth_ids"][0])
        response = helpers.make_request(session, "/api/v1/dataset/user")
        assert response.code == 200
        assert len(user_datasets) == len(response.data["datasets"])
        assert set(entry["id"] for entry in response.data["datasets"]) == set(user_datasets)


def test_get_dataset_get_permissions(mdb):
    """
    Confirm that anyone can access any dataset.

    Tests:
      * Get random dataset, confirm that everyone can access it
    """
    orders = list(mdb["datasets"].aggregate([{"$sample": {"size": 2}}]))
    for order in orders:
        responses = helpers.make_request_all_roles(f'/api/v1/dataset/{order["_id"]}', ret_json=True)
        for response in responses:
            assert response.data["dataset"]
            assert response.code == 200


def test_get_dataset(mdb):
    """
    Confirm that datasets are returned correctly.

    Tests:
      * Confirm that the correct dataset is returned
      * Confirm that the dataset is not listed in ``related``
    """
    session = requests.Session()

    order_id = helpers.add_order()
    ds_id = helpers.add_dataset(order_id)
    ds_id2 = helpers.add_dataset(order_id)
    coll_id = helpers.add_collection([ds_id])
    coll_id2 = helpers.add_collection([ds_id])

    helpers.as_user(session, helpers.USERS["edit"])
    order_data = mdb["orders"].find_one({"_id": order_id})

    response = helpers.make_request(session, f"/api/v1/dataset/{ds_id}")
    assert response.code == 200
    result = response.data["dataset"]
    assert result["order"]["id"] == str(order_id)
    assert set(entry["id"] for entry in result["related"]) == {str(ds_id2)}
    assert set(entry["id"] for entry in result["collections"]) == {str(coll_id), str(coll_id2)}
    assert set(entry["id"] for entry in result["authors"]) == set(
        str(entry) for entry in order_data["authors"]
    )
    assert set(entry["id"] for entry in result["generators"]) == set(
        str(entry) for entry in order_data["generators"]
    )
    assert result["organisation"]["id"] == str(order_data["organisation"])
    assert set(entry["id"] for entry in result["editors"]) == set(
        str(entry) for entry in order_data["editors"]
    )

    helpers.as_user(session, helpers.USERS["base"])
    order_data = mdb["orders"].find_one({"_id": order_id})

    response = helpers.make_request(session, f"/api/v1/dataset/{ds_id}")
    assert response.code == 200
    result = response.data["dataset"]
    assert "order" not in result
    assert set(entry["id"] for entry in result["related"]) == {str(ds_id2)}
    assert set(entry["id"] for entry in result["collections"]) == {str(coll_id), str(coll_id2)}
    assert set(entry["id"] for entry in result["authors"]) == set(
        str(entry) for entry in order_data["authors"]
    )
    assert set(entry["id"] for entry in result["generators"]) == set(
        str(entry) for entry in order_data["generators"]
    )
    assert result["organisation"]["id"] == str(order_data["organisation"])
    assert "editors" not in result

    mdb["orders"].delete_one({"_id": order_id})
    mdb["datasets"].delete_one({"_id": ds_id})
    mdb["datasets"].delete_one({"_id": ds_id2})
    mdb["collections"].delete_one({"_id": coll_id})
    mdb["collections"].delete_one({"_id": coll_id2})


def test_get_dataset_bad():
    """
    Confirm that non-existing datasets return 404.

    Tests:
      * Generate random identifiers, confirm they return 404
    """
    session = requests.Session()
    for _ in range(5):
        response = helpers.make_request(session, f"/api/v1/dataset/{uuid.uuid4().hex}")
        assert response.code == 404
        assert not response.data

    for _ in range(5):
        response = helpers.make_request(session, f"/api/v1/dataset/{helpers.random_string()}")
        assert response.code == 404
        assert not response.data


def test_delete_dataset_permissions(mdb):
    """
    Confirm that permissions for deleting datasets are correct.

    Checks:
      * DATA_MANAGER can delete any dataset
      * DATA_EDIT can delete dataset where they are editors (in the order)
      * Other users cannot delete any dataset, even if they are editors
    """
    order_id = helpers.add_order()
    ds_id = helpers.add_dataset(order_id)
    session = requests.Session()

    for role in helpers.USERS:
        helpers.as_user(session, helpers.USERS[role])
        response = helpers.make_request(
            session, f"/api/v1/dataset/{ds_id}", method="DELETE", ret_json=True
        )
        if role in ("edit", "data", "root"):
            assert response.code == 200
            ds_id = helpers.add_dataset(order_id)
        elif role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    edit_user = mdb["users"].find_one({"auth_ids": helpers.USERS["edit"]})
    mdb["orders"].update_one({"_id": order_id}, {"$pull": {"editors": edit_user["_id"]}})
    helpers.as_user(session, helpers.USERS["edit"])
    response = helpers.make_request(
        session, f"/api/v1/dataset/{ds_id}", method="DELETE", ret_json=True
    )
    assert response.code == 403
    assert not response.data

    base_user = mdb["users"].find_one({"auth_ids": helpers.USERS["base"]})
    mdb["orders"].update_one({"_id": order_id}, {"$push": {"editors": base_user["_id"]}})
    helpers.as_user(session, helpers.USERS["base"])
    response = helpers.make_request(
        session, f"/api/v1/dataset/{ds_id}", method="DELETE", ret_json=True
    )
    assert response.code == 403
    assert not response.data


def test_delete_dataset(mdb):
    """
    Confirm that datasets are deleted correctly.

    Tests:
      * Check that datasets are deleted correctly
      * Check that references to the dataset are deleted in orders and collections
      * Check that logs are created correctly
    """
    session = requests.Session()
    order_id = helpers.add_order()
    ds_id = helpers.add_dataset(order_id)
    coll_id = helpers.add_collection([ds_id])
    coll_id2 = helpers.add_collection([ds_id])

    helpers.as_user(session, helpers.USERS["edit"])
    response = helpers.make_request(session, f"/api/v1/dataset/{ds_id}", method="DELETE")
    assert response.code == 200
    assert not mdb["datasets"].find_one({"_id": ds_id})
    assert (
        mdb["logs"].count_documents({"data_type": "dataset", "action": "delete", "data._id": ds_id})
        == 1
    )
    assert not mdb["orders"].find_one({"datasets": ds_id})
    assert (
        mdb["logs"].count_documents(
            {
                "data_type": "order",
                "comment": "Dataset deleted",
                "action": "edit",
                "data._id": order_id,
            }
        )
        == 1
    )
    assert not mdb["collections"].find_one({"datasets": ds_id})
    assert (
        mdb["logs"].count_documents(
            {
                "data_type": "collection",
                "comment": "Dataset deleted",
                "action": "edit",
                "data._id": {"$in": (coll_id, coll_id2)},
            }
        )
        == 2
    )

    # clean up added datasets
    for ds in mdb["datasets"].find(TEST_LABEL):
        response = helpers.make_request(session, f'/api/v1/dataset/{ds["_id"]}', method="DELETE")
        if response.code == 200:
            assert not mdb["datasets"].find_one({"_id": ds["_id"]})
            assert not mdb["orders"].find_one({"datasets": ds["_id"]})
            assert not mdb["collections"].find_one({"datasets": ds["_id"]})

    helpers.as_user(session, helpers.USERS["data"])
    # clean up added datasets
    for ds in mdb["datasets"].find(TEST_LABEL):
        response = helpers.make_request(session, f'/api/v1/dataset/{ds["_id"]}', method="DELETE")
        assert response.code == 200
        assert not mdb["datasets"].find_one({"_id": ds["_id"]})
        assert not mdb["orders"].find_one({"datasets": ds["_id"]})
        assert not mdb["collections"].find_one({"datasets": ds["_id"]})


def test_delete_bad():
    """Confirm that bad identifiers return 404."""
    session = requests.Session()
    helpers.as_user(session, helpers.USERS["data"])
    for _ in range(3):
        ds_uuid = helpers.random_string()
        response = helpers.make_request(session, f"/api/v1/dataset/{ds_uuid}", method="DELETE")
        assert response.code == 404
        assert not response.data

        ds_uuid = uuid.uuid4()
        response = helpers.make_request(session, f"/api/v1/dataset/{ds_uuid}", method="DELETE")
        assert response.code == 404
        assert not response.data


def test_dataset_update_permissions(mdb):
    """
    Confirm that permissions for updating datasets are correct.

    Checks:
      * DATA_MANAGER can update any dataset
      * DATA_EDIT can update datasets where they are editors (in the order)
      * Other users cannot update any dataset, even if they are editors
    """
    session = requests.Session()
    order_id = helpers.add_order()
    ds_id = helpers.add_dataset(order_id)

    indata = {"dataset": {"title": "Updated dataset permissions title"}}
    responses = helpers.make_request_all_roles(
        f"/api/v1/dataset/{ds_id}", method="PATCH", data=indata
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 200
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"dataset": {"title": "Updated dataset permissions title 2"}}
    edit_user = mdb["users"].find_one({"auth_ids": helpers.USERS["edit"]})
    mdb["orders"].update_one({"_id": order_id}, {"$pull": {"editors": edit_user["_id"]}})
    helpers.as_user(session, helpers.USERS["edit"])
    response = helpers.make_request(
        session, f"/api/v1/dataset/{ds_id}", method="PATCH", data=indata
    )
    assert response.code == 403
    assert not response.data

    base_user = mdb["users"].find_one({"auth_ids": helpers.USERS["base"]})
    mdb["orders"].update_one({"_id": order_id}, {"$push": {"editors": base_user["_id"]}})
    helpers.as_user(session, helpers.USERS["base"])
    response = helpers.make_request(
        session, f"/api/v1/dataset/{ds_id}", method="PATCH", data=indata
    )
    assert response.code == 403
    assert not response.data


def test_dataset_update_empty(dataset_for_tests):
    """Confirm response 400 to an empty update request."""
    ds_uuid = dataset_for_tests
    indata = {}
    responses = helpers.make_request_all_roles(
        f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 400
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data


def test_dataset_update_data(mdb):
    """
    Confirm that the dataset is updated correctly.

    Tests:
      * All fields are correctly updated
      * Confirm that description is escaped
      * Confirm that a log entry is created
    """
    session = requests.Session()
    ds_id = helpers.add_dataset(helpers.add_order())

    indata = {
        "dataset": {
            "description": "<br />",
            "title": "Test title - dataset update data",
        }
    }
    indata["dataset"].update(TEST_LABEL)

    helpers.as_user(session, helpers.USERS["data"])

    response = helpers.make_request(
        session, f"/api/v1/dataset/{ds_id}", method="PATCH", data=indata
    )
    assert response.code == 200
    assert not response.data

    dataset = mdb["datasets"].find_one({"_id": ds_id})
    assert dataset["title"] == indata["dataset"]["title"]
    assert dataset["description"] == "&lt;br /&gt;"
    assert mdb["logs"].find_one({"data._id": ds_id, "action": "edit", "data_type": "dataset"})


def test_dataset_update_bad(dataset_for_tests):
    """Confirm that bad requests will be rejected."""
    indata = {"dataset": {"title": "Updated title"}}
    ds_uuid = helpers.random_string()
    responses = helpers.make_request_all_roles(
        f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 404
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
            assert not response.data

    ds_uuid = uuid.uuid4().hex
    responses = helpers.make_request_all_roles(
        f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 404
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
            assert not response.data

    ds_uuid = dataset_for_tests
    session = requests.Session()
    helpers.as_user(session, helpers.USERS["data"])
    indata = {"title": ""}
    response = helpers.make_request(
        session, f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
    )
    assert response.code == 400
    assert not response.data

    indata = {"dataset": {"extra": "asd"}}
    response = helpers.make_request(
        session, f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
    )
    assert response.code == 400
    assert not response.data

    indata = {"dataset": {"timestamp": "asd"}}
    response = helpers.make_request(
        session, f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
    )
    assert response.code == 400
    assert not response.data


def test_get_dataset_logs_permissions(mdb):
    """
    Get dataset logs.

    Assert that DATA_MANAGEMENT or user in editors is required.
    """
    dataset_data = mdb["datasets"].aggregate([{"$sample": {"size": 1}}]).next()
    order_data = mdb["orders"].find_one({"datasets": dataset_data["_id"]})
    user_data = mdb["users"].find_one({"$or": [{"_id": {"$in": order_data["editors"]}}]})
    responses = helpers.make_request_all_roles(
        f'/api/v1/dataset/{dataset_data["_id"]}/log', ret_json=True
    )
    for response in responses:
        if response.role in ("data", "root"):
            assert response.code == 200
            assert "logs" in response.data
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    session = requests.Session()

    helpers.as_user(session, user_data["auth_ids"][0])
    response = helpers.make_request(
        session, f'/api/v1/dataset/{dataset_data["_id"]}/log', ret_json=True
    )

    assert response.code == 200
    assert "logs" in response.data


def test_get_dataset_logs(mdb):
    """
    Request the logs for multiple datasets.

    Confirm that the logs contain only the intended fields.
    """
    session = requests.session()
    datasets = mdb["datasets"].aggregate([{"$sample": {"size": 2}}])
    for dataset in datasets:
        logs = list(mdb["logs"].find({"data_type": "dataset", "data._id": dataset["_id"]}))
        helpers.as_user(session, helpers.USERS["data"])
        response = helpers.make_request(
            session, f'/api/v1/dataset/{dataset["_id"]}/log', ret_json=True
        )
        assert response.data["data_type"] == "dataset"
        assert response.data["entry_id"] == str(dataset["_id"])
        assert len(response.data["logs"]) == len(logs)
        assert response.code == 200


def test_info_add_dataset():
    """Confirm that the redirect information works as intended."""
    session = requests.session()
    helpers.as_user(session, helpers.USERS["data"])
    response = helpers.make_request(session, "/api/v1/dataset", ret_json=False, method="POST")
    assert response.data == "Use http://localhost:5000/api/v1/order/-identifier-/dataset instead"
