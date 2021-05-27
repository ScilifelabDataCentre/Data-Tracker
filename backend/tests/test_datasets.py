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
    delete_dataset,
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
    user_uuids = list(
        itertools.chain.from_iterable(order["editors"] for order in orders)
    )
    users = mdb["users"].find({"_id": {"$in": list(user_uuids)}})
    for user in users:
        user_orders = list(
            mdb["orders"].find({"editors": user["_id"]}, {"datasets": 1})
        )
        user_datasets = list(
            itertools.chain.from_iterable(order["datasets"] for order in user_orders)
        )
        user_datasets = [str(uuid) for uuid in user_datasets]

        helpers.as_user(session, user["auth_ids"][0])
        response = helpers.make_request(session, "/api/v1/dataset/user")
        assert response.code == 200
        assert len(user_datasets) == len(response.data["datasets"])
        assert set(entry["id"] for entry in response.data["datasets"]) == set(
            user_datasets
        )


def test_list_user_datasets_no_datasets():
    """
    Confirm that users with no datasets get the correct response.

    Tests:

      * Select a few users, confirm that no datasets are returned as intended
    """
    # *::testers should have no datasets
    responses = helpers.make_request_all_roles("/api/v1/dataset/user", ret_json=True)
    for response in responses:
        if response.role != "no-login":
            assert len(response.data["datasets"]) == 0


def test_get_dataset_get_permissions(mdb):
    """Test permissions for requesting a dataset."""
    orders = list(mdb["datasets"].aggregate([{"$sample": {"size": 2}}]))
    for order in orders:
        responses = helpers.make_request_all_roles(
            f'/api/v1/dataset/{order["_id"]}', ret_json=True
        )
        for response in responses:
            assert response.data["dataset"]
            assert response.code == 200


def test_get_dataset(mdb):
    """Request multiple datasets by uuid, one at a time."""
    session = requests.Session()
    for _ in range(10):
        orig = mdb["datasets"].aggregate([{"$sample": {"size": 1}}]).next()
        response = helpers.make_request(session, f'/api/v1/dataset/{orig["_id"]}')
        assert response[1] == 200
        requested = response[0]["dataset"]
        assert str(orig["_id"]) == requested["id"]
        assert requested["id"] not in requested["related"]


def test_get_dataset_bad():
    """
    Request datasets using bad identifiers.

    All are expected to return 404.
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


def test_delete_dataset(mdb):
    """
    Add and delete datasets.

    * Check permissions.
    * Delete orders added by the add tests.
    * Confirm that related dataset entries in orders and projects are deleted.
    * Check that logs are created correctly.
    """
    session = requests.Session()

    uuids = [helpers.add_dataset_full() for _ in range(5)]

    datasets = list(mdb["datasets"].find(TEST_LABEL))
    if not datasets:
        assert False
    i = 0
    while i < len(datasets):
        for role in helpers.USERS:
            helpers.as_user(session, helpers.USERS[role])
            order = mdb["orders"].find_one({"datasets": datasets[i]["_id"]})
            collections = list(
                mdb["collections"].find({"datasets": datasets[i]["_id"]})
            )
            response = helpers.make_request(
                session, f'/api/v1/dataset/{datasets[i]["_id"]}', method="DELETE"
            )
            current_user = mdb["users"].find_one({"auth_ids": helpers.USERS[role]})
            if role == "no-login":
                assert response.code == 401
                assert not response.data
            # only data managers or owners may delete datasets
            elif role in ("data", "root") or current_user["_id"] in order["editors"]:
                assert response.code == 200
                assert not response.data
                # confirm that dataset does not exist in mdb and that a log has been created
                assert not mdb["datasets"].find_one({"_id": datasets[i]["_id"]})
                assert mdb["logs"].find_one(
                    {
                        "data._id": datasets[i]["_id"],
                        "action": "delete",
                        "data_type": "dataset",
                    }
                )
                # confirm that no references to the dataset exist in orders or collection
                assert not list(mdb["orders"].find({"datasets": datasets[i]["_id"]}))
                assert not list(
                    mdb["collections"].find({"datasets": datasets[i]["_id"]})
                )
                # confirm that the removal of the references are logged.
                assert mdb["logs"].find_one(
                    {
                        "data._id": order["_id"],
                        "action": "edit",
                        "data_type": "order",
                        "comment": f'Deleted dataset {datasets[i]["_id"]}',
                    }
                )
                p_log = list(
                    mdb["logs"].find(
                        {
                            "action": "edit",
                            "data_type": "collection",
                            "comment": f'Deleted dataset {datasets[i]["_id"]}',
                        }
                    )
                )
                assert len(p_log) == len(collections)
                i += 1
                if i >= len(datasets):
                    break
            else:
                assert response.code == 403
                assert not response.data

    assert i > 0
    for uuid_group in uuids:
        delete_dataset(*uuid_group)


def test_delete_bad():
    """
    Bad deletion requests.

    Should require at least Steward.
    """
    session = requests.Session()
    helpers.as_user(session, helpers.USERS["data"])
    for _ in range(3):
        ds_uuid = helpers.random_string()
        response = helpers.make_request(session, f"/api/v1/dataset/{ds_uuid}", method="DELETE")
        assert response.code == 404
        assert not response.data
        ds_uuid = uuid.uuid4().hex
        response = helpers.make_request(session, f"/api/v1/dataset/{ds_uuid}", method="DELETE")
        assert response.code == 404
        assert not response.data


def test_dataset_update_permissions(dataset_for_tests):
    """
    Test the permissions for the request.

    Should require at least Steward or being the owner of the dataset.
    """
    ds_uuid = dataset_for_tests
    indata = {"title": "Updated title"}
    responses = helpers.make_request_all_roles(
        f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 200
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data


def test_dataset_update_empty(dataset_for_tests):
    """
    Confirm response 400 to an empty update request

    Should require at least Steward or being the owner of the dataset.
    """
    ds_uuid = dataset_for_tests
    indata = {}
    responses = helpers.make_request_all_roles(
        f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 200
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data


def test_dataset_update(mdb, dataset_for_tests):
    """
    Update a dataset multiple times. Confirm that the update is done correctly.

    Should require at least Steward.
    """
    ds_uuid = dataset_for_tests
    indata = {
        "description": "Test description - updated",
        "title": "Test title - updated",
    }
    indata.update(TEST_LABEL)

    session = requests.Session()
    helpers.as_user(session, helpers.USERS["data"])

    response = helpers.make_request(
        session, f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
    )
    assert response.code == 200
    assert not response.data

    dataset = mdb["datasets"].find_one({"_id": ds_uuid})
    for field in indata:
        assert dataset[field] == indata[field]
    assert mdb["logs"].find_one(
        {"data._id": ds_uuid, "action": "edit", "data_type": "dataset"}
    )


def test_dataset_update_bad(dataset_for_tests):
    """
    Confirm that bad requests will be rejected.

    Should require at least Steward.
    """
    for _ in range(2):
        indata = {"title": "Updated title"}
        ds_uuid = helpers.random_string()
        responses = helpers.make_request_all_roles(
            f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
        )
        for response in responses:
            if response.role in ("base", "edit", "data", "root"):
                assert response.code == 404
            elif response.role == "no-login":
                assert response.code == 401
            else:
                assert response.code == 404
                assert not response.data

        ds_uuid = uuid.uuid4().hex
        responses = helpers.make_request_all_roles(
            f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
        )
        for response in responses:
            if response.role in ("base", "edit", "data", "root"):
                assert response.code == 404
            elif response.role == "no-login":
                assert response.code == 401
            else:
                assert response.code == 404
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

    indata = {"extra": "asd"}
    response = helpers.make_request(
        session, f"/api/v1/dataset/{ds_uuid}", method="PATCH", data=indata
    )
    assert response.code == 400
    assert not response.data

    indata = {"timestamp": "asd"}
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
    user_data = mdb["users"].find_one(
        {"$or": [{"_id": {"$in": order_data["editors"]}}]}
    )
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
        logs = list(
            mdb["logs"].find({"data_type": "dataset", "data._id": dataset["_id"]})
        )
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
    assert (
        response.data
        == "Use http://localhost:5000/api/v1/order/-identifier-/dataset instead"
    )
