"""Tests for collection requests."""
import uuid
import requests

import utils

# pylint: disable=unused-import
from helpers import (
    make_request,
    as_user,
    make_request_all_roles,
    USERS,
    random_string,
    mdb,
    TEST_LABEL,
    collection_for_tests,
    add_dataset,
    delete_dataset,
)

# pylint: enable=unused-import
# pylint: disable=redefined-outer-name


def test_get_collection_permissions(mdb):
    """Test permissions for requesting a collection."""
    collection = list(mdb["collections"].aggregate([{"$sample": {"size": 1}}]))[0]

    responses = make_request_all_roles(
        f'/api/v1/collection/{collection["_id"]}', ret_json=True
    )
    for response in responses:
        assert response.code == 200


def test_get_collection(mdb):
    """Request multiple collections by uuid, one at a time."""
    session = requests.Session()
    for _ in range(3):
        collection = list(mdb["collections"].aggregate([{"$sample": {"size": 1}}]))[0]
        collection["_id"] = str(collection["_id"])
        proj_owner = mdb["users"].find_one({"_id": {"$in": collection["editors"]}})
        collection["editors"] = [str(entry) for entry in collection["editors"]]
        collection["datasets"] = [str(entry) for entry in collection["datasets"]]
        collection = utils.convert_keys_to_camel(collection)
        as_user(session, USERS["base"])
        response = make_request(session, f'/api/v1/collection/{collection["_id"]}')
        assert response.code == 200
        for field in collection:
            if field == "datasets":
                for i, ds_uuid in enumerate(collection[field]):
                    assert ds_uuid == response.data["collection"][field][i]["_id"]
            elif field == "editors":
                continue
            else:
                assert collection[field] == response.data["collection"][field]

        as_user(session, proj_owner["auth_ids"][0])
        response = make_request(session, f'/api/v1/collection/{collection["_id"]}')
        assert response.code == 200
        print(collection)
        for field in collection:
            if field in ("datasets", "editors"):
                entries = [entry["_id"] for entry in response.data["collection"][field]]
                assert len(collection[field]) == len(entries)
                for i, ds_uuid in enumerate(collection[field]):
                    assert ds_uuid in entries
            else:
                assert collection[field] == response.data["collection"][field]

        as_user(session, USERS["root"])
        response = make_request(session, f'/api/v1/collection/{collection["_id"]}')
        assert response.code == 200
        for field in collection:
            if field in ("datasets", "editors"):
                entries = [entry["_id"] for entry in response.data["collection"][field]]
                assert len(collection[field]) == len(entries)
                for i, ds_uuid in enumerate(collection[field]):
                    assert ds_uuid in entries
            else:
                assert collection[field] == response.data["collection"][field]


def test_get_collection_bad():
    """
    Request collections using bad identifiers.

    All are expected to return 404.
    """
    session = requests.Session()
    for _ in range(2):
        response = make_request(session, f"/api/v1/collection/{uuid.uuid4().hex}")
        assert response.code == 404
        assert not response.data

    for _ in range(2):
        response = make_request(session, f"/api/v1/collection/{random_string()}")
        assert response.code == 404
        assert not response.data


def test_add_collection_permissions(mdb):
    """
    Add a collection.

    Test permissions.
    """
    indata = {"title": "Test title"}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(
        "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 200
            assert "_id" in response.data
            assert len(response.data["_id"]) == 36
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    user_info = mdb["users"].find_one({"auth_ids": USERS["base"]})
    indata.update({"editors": [str(user_info["_id"])]})
    responses = make_request_all_roles(
        "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        print(response.role)
        if response.role in ("edit", "root", "data"):
            assert response.code == 200
            assert "_id" in response.data
            assert len(response.data["_id"]) == 36
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_add_collection(mdb):
    """
    Add a collection.

    Confirm:
    * fields are set correctly
    * logs are created
    """
    dataset_info = next(mdb["datasets"].aggregate([{"$sample": {"size": 1}}]))
    order_info = mdb["orders"].find_one({"datasets": dataset_info["_id"]})
    session = requests.Session()
    user_info = mdb["users"].find_one({"_id": {"$in": order_info["editors"]}})

    as_user(session, user_info["auth_ids"][0])

    indata = {
        "description": "Test description",
        "editors": [str(user_info["_id"])],
        "title": "Test title",
        "datasets": [str(dataset_info["_id"])],
    }
    indata.update(TEST_LABEL)

    response = make_request(
        session, "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    assert response.code == 200
    assert "_id" in response.data
    assert len(response.data["_id"]) == 36
    collection = mdb["collections"].find_one({"_id": uuid.UUID(response.data["_id"])})
    assert collection["description"] == indata["description"]
    assert str(collection["editors"][0]) == indata["editors"][0]
    assert collection["title"] == indata["title"]
    assert str(collection["datasets"][0]) == indata["datasets"][0]

    # log
    assert mdb["logs"].find_one(
        {
            "data._id": uuid.UUID(response.data["_id"]),
            "data_type": "collection",
            "user": user_info["_id"],
            "action": "add",
        }
    )

    as_user(session, USERS["data"])

    response = make_request(
        session, "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    assert response.code == 200
    assert "_id" in response.data
    assert len(response.data["_id"]) == 36
    collection = mdb["collections"].find_one({"_id": uuid.UUID(response.data["_id"])})
    assert collection["description"] == indata["description"]
    assert str(collection["editors"][0]) == indata["editors"][0]
    assert collection["title"] == indata["title"]
    assert str(collection["datasets"][0]) == indata["datasets"][0]

    data_user = mdb["users"].find_one({"auth_ids": USERS["data"]})

    # log
    assert mdb["logs"].find_one(
        {
            "data._id": uuid.UUID(response.data["_id"]),
            "data_type": "collection",
            "user": data_user["_id"],
            "action": "add",
        }
    )


def test_add_collection_bad():
    """
    Add a default dataset using / POST.

    Bad requests.
    """
    indata = {"title": ""}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(
        "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
            assert not response.data
        elif response.role in ("root", "edit", "data"):
            assert response.code == 400
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    indata = {}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(
        "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
            assert not response.data
        elif response.role in ("root", "edit", "data"):
            assert response.code == 400
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    indata = {"bad_tag": "content", "title": "title"}

    indata.update(TEST_LABEL)

    responses = make_request_all_roles(
        "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
            assert not response.data
        elif response.role in ("root", "edit", "data"):
            assert response.code == 400
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    indata = {
        "description": "Test description",
        "owners": [str(uuid.uuid4())],
        "title": "Test title",
    }
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(
        "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
            assert not response.data
        elif response.role in ("root", "edit", "data"):
            assert response.code == 400
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    session = requests.Session()
    as_user(session, USERS["data"])
    indata = {
        "_id": str(uuid.uuid4()),
        "owners": [str(uuid.uuid4())],
        "title": "Test title",
    }
    indata.update(TEST_LABEL)
    response = make_request(
        session, "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    assert response.code == 403
    assert not response.data

    indata = {"datasets": [str(uuid.uuid4())], "title": "Test title"}
    indata.update(TEST_LABEL)
    response = make_request(
        session, "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    assert response.code == 400


def test_update_collection_permissions(mdb, collection_for_tests):
    """
    Update a collection.

    Test permissions.
    """
    # TODO: test more situations for new permissions
    session = requests.Session()

    collection_uuid = collection_for_tests
    print(mdb["collections"].find_one({"_id": collection_uuid}))

    for role in USERS:
        as_user(session, USERS[role])
        indata = {"title": f"Test title - updated by {role}"}
        response = make_request(
            session,
            f"/api/v1/collection/{collection_uuid}",
            method="PATCH",
            data=indata,
            ret_json=True,
        )
        if role in ("edit", "data", "root"):
            assert response.code == 200
            assert not response.data
            new_collection = mdb["collections"].find_one({"_id": collection_uuid})
            assert new_collection["title"] == f"Test title - updated by {role}"
        elif role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_update_collection(mdb):
    """
    Update existing collections.

    1. Add a new dataset
    2. Add dataset (and other fields) for existing collection using edit user
    3. Confirm correct update
    4. Check that log was created
    5. Perform update as data user
    6. Confirm correct update
    7. Confirm that log was created
    8. Clean up
    """
    uuids = add_dataset()
    collection_info = mdb["collections"].find_one({"_id": uuids[2]})
    user_info = mdb["users"].find_one({"auth_ids": USERS["edit"]})

    indata = {
        "description": "Test description updated",
        "editors": [str(collection_info["editors"][0])],
        "title": "Test title updated",
        "datasets": [str(uuids[1])],
    }
    indata.update(TEST_LABEL)

    session = requests.Session()
    as_user(session, USERS["edit"])

    response = make_request(
        session,
        f'/api/v1/collection/{collection_info["_id"]}',
        method="PATCH",
        data=indata,
        ret_json=True,
    )
    assert response.code == 200
    collection = mdb["collections"].find_one({"_id": collection_info["_id"]})
    assert collection["description"] == indata["description"]
    assert str(collection["editors"][0]) == indata["editors"][0]
    assert collection["title"] == indata["title"]
    assert str(collection["datasets"][0]) == indata["datasets"][0]

    # log
    assert mdb["logs"].find_one(
        {
            "data._id": collection_info["_id"],
            "data_type": "collection",
            "user": user_info["_id"],
            "action": "edit",
        }
    )

    as_user(session, USERS["data"])
    user_info = mdb["users"].find_one({"auth_ids": USERS["data"]})

    indata = {
        "description": "Test description updated2",
        "editors": [str(user_info["_id"])],
        "title": "Test title updated",
        "datasets": [str(uuids[1]), str(uuids[1])],
    }
    indata.update(TEST_LABEL)

    response = make_request(
        session,
        f'/api/v1/collection/{collection_info["_id"]}',
        method="PATCH",
        data=indata,
        ret_json=True,
    )
    assert response.code == 200
    collection = mdb["collections"].find_one({"_id": collection_info["_id"]})
    assert collection["description"] == indata["description"]
    assert str(collection["editors"][0]) == indata["editors"][0]
    assert collection["title"] == indata["title"]
    assert str(collection["datasets"][0]) == indata["datasets"][0]

    # log
    assert mdb["logs"].find_one(
        {
            "data._id": collection_info["_id"],
            "data_type": "collection",
            "user": user_info["_id"],
            "action": "edit",
        }
    )
    delete_dataset(*uuids)


def test_update_collection_bad(mdb):
    """
    Update an existing collection.

    Bad requests.
    """
    uuids = add_dataset()
    collection_info = mdb["collections"].find_one({"_id": uuids[2]})

    indata = {"bad_tag": "value"}

    responses = make_request_all_roles(
        f'/api/v1/collection/{collection_info["_id"]}',
        method="PATCH",
        data=indata,
        ret_json=True,
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 400
            assert not response.data
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    indata = {
        "description": "Test description",
        "owners": [str(uuid.uuid4())],
        "title": "Test title",
    }

    responses = make_request_all_roles(
        f'/api/v1/collection/{collection_info["_id"]}',
        method="PATCH",
        data=indata,
        ret_json=True,
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 400
            assert not response.data
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    for _ in range(2):
        indata = {"title": "Test title"}
        responses = make_request_all_roles(
            f"/api/v1/collection/{uuid.uuid4()}",
            method="PATCH",
            data=indata,
            ret_json=True,
        )
        for response in responses:
            if response.role == "no-login":
                assert response.code == 401
                assert not response.data
            elif response.role in ("edit", "root", "data"):
                assert response.code == 404
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        indata = {"title": "Test title"}
        responses = make_request_all_roles(
            f"/api/v1/collection/{random_string()}",
            method="PATCH",
            data=indata,
            ret_json=True,
        )
        for response in responses:
            if response.role == "no-login":
                assert response.code == 401
                assert not response.data
            elif response.role in ("edit", "root", "data"):
                assert response.code == 404
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

    delete_dataset(*uuids)


def test_delete_collection(mdb):
    """
    Add and delete collections.

    * Check permissions.
    * Delete collections added by the add tests.
    * Confirm that related datasets are deleted.
    * Check that logs are created correctly.
    """
    session = requests.Session()

    # must be updated if TEST_LABEL is modified
    collections = list(mdb["collections"].find({"extra.testing": "yes"}))
    i = 0
    while i < len(collections):
        for role in USERS:
            as_user(session, USERS[role])
            response = make_request(
                session, f'/api/v1/collection/{collections[i]["_id"]}', method="DELETE"
            )
            if role in ("data", "root"):
                assert response.code == 200
                assert not response.data
                assert not mdb["collections"].find_one({"_id": collections[i]["_id"]})
                assert mdb["logs"].find_one(
                    {
                        "data._id": collections[i]["_id"],
                        "action": "delete",
                        "data_type": "collection",
                    }
                )
                i += 1
                if i >= len(collections):
                    break
            elif role == "no-login":
                assert response.code == 401
                assert not response.data
            else:
                current_user = mdb["users"].find_one({"auth_id": USERS[role]})
                if current_user["_id"] in collections[i]["owners"]:
                    assert response.code == 200
                    assert not response.data
                    assert not mdb["collections"].find_one(
                        {"_id": collections[i]["_id"]}
                    )
                    assert mdb["logs"].find_one(
                        {
                            "data._id": collections[i]["_id"],
                            "action": "delete",
                            "data_type": "collection",
                        }
                    )
                    i += 1
                    if i >= len(collections):
                        break

                else:
                    assert response.code == 403
                    assert not response.data

    as_user(session, USERS["edit"])
    response = make_request(
        session, "/api/v1/collection", data={"title": "tmp"}, method="POST"
    )
    assert response.code == 200
    response = make_request(
        session, f'/api/v1/collection/{response.data["_id"]}', method="DELETE"
    )
    assert response.code == 200
    assert not response.data


def test_delete_collection_bad():
    """Attempt bad collection delete requests."""
    session = requests.Session()

    as_user(session, USERS["data"])
    for _ in range(2):
        response = make_request(
            session, f"/api/v1/collection/{random_string()}", method="DELETE"
        )
    assert response.code == 404
    assert not response.data

    for _ in range(2):
        response = make_request(
            session, f"/api/v1/collection/{uuid.uuid4()}", method="DELETE"
        )
    assert response.code == 404
    assert not response.data


def test_list_collections(mdb):
    """
    Request a list of all collections.

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles("/api/v1/collection", ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data["collections"]) == mdb["collections"].count_documents(
            {}
        )


def test_get_collection_logs_permissions(mdb):
    """
    Get collection logs.

    Assert that DATA_MANAGEMENT or user in owners is required.
    """
    collection_data = mdb["collections"].aggregate([{"$sample": {"size": 1}}]).next()
    user_data = mdb["users"].find_one({"_id": {"$in": collection_data["editors"]}})
    responses = make_request_all_roles(
        f'/api/v1/collection/{collection_data["_id"]}/log', ret_json=True
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

    as_user(session, user_data["auth_ids"][0])
    response = make_request(
        session, f'/api/v1/collection/{collection_data["_id"]}/log', ret_json=True
    )

    assert response.code == 200
    assert "logs" in response.data


def test_get_collection_logs(mdb):
    """
    Request the logs for multiple collections.

    Confirm that the logs contain only the intended fields.
    """
    session = requests.session()
    collections = mdb["collections"].aggregate([{"$sample": {"size": 2}}])
    for collection in collections:
        logs = list(
            mdb["logs"].find({"data_type": "collection", "data._id": collection["_id"]})
        )
        as_user(session, USERS["data"])
        response = make_request(
            session, f'/api/v1/collection/{collection["_id"]}/log', ret_json=True
        )
        assert response.data["dataType"] == "collection"
        assert response.data["entryId"] == str(collection["_id"])
        assert len(response.data["logs"]) == len(logs)
        assert response.code == 200
