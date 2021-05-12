"""Tests for collection requests."""
import uuid

import requests

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import
from helpers import (
    TEST_LABEL,
    USERS,
    add_dataset,
    as_user,
    collection_for_tests,
    delete_dataset,
    make_request,
    make_request_all_roles,
    mdb,
    random_string,
)

import helpers

import utils


def test_list_collections(mdb):
    """Request a list of all collections."""
    responses = make_request_all_roles("/api/v1/collection", ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data["collections"]) == mdb["collections"].count_documents(
            {}
        )
        assert set(response.data["collections"][0].keys()) == {
            "id",
            "title",
            "tags",
            "properties",
        }


def test_add_collection_permissions(mdb):
    """
    Test permissions for adding a collection.

    * any user with ``DATA_MANAGEMENT`` can add a collection
    """
    indata = {"collection": {"title": "Test title"}}
    indata["collection"].update(TEST_LABEL)

    responses = make_request_all_roles(
        "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 200
            assert "id" in response.data
            assert len(response.data["id"]) == 36
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_add_collection_data(mdb):
    """
    Test the functionality for adding collections.

    Checks:
    * fields are set correctly
    * logs are created
    * logs contain the relevant data
    """
    ds_id = next(mdb["datasets"].aggregate([{"$sample": {"size": 1}}]))["_id"]
    order_info = mdb["orders"].find_one({"datasets": ds_id})
    user_info = mdb["users"].find_one({"_id": {"$in": order_info["editors"]}})

    session = requests.Session()
    as_user(session, user_info["auth_ids"][0])

    # add data
    indata = {
        "collection": {
            "description": "Test description",
            "editors": [str(user_info["_id"])],
            "title": "Test title",
            "datasets": [str(ds_id)],
            "tags": [],
            "properties": {
                "Source": "Added from test",
            },
        }
    }
    indata["collection"].update(TEST_LABEL)
    response = make_request(
        session, "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    assert response.code == 200
    assert "id" in response.data
    assert len(response.data["id"]) == 36

    added_id = uuid.UUID(response.data["id"])

    # validate added data
    collection = mdb["collections"].find_one({"_id": added_id})
    utils.prepare_response(collection)
    for field in ("editors", "datasets"):
        collection[field] = [str(entry) for entry in collection[field]]
    for field in indata["collection"]:
        assert collection[field] == indata["collection"][field]

    # validate log
    log_query = {
        "data._id": added_id,
        "data_type": "collection",
        "user": user_info["_id"],
        "action": "add",
    }
    log_entry = mdb["logs"].find_one(log_query)
    assert log_entry
    for field in ("editors", "datasets"):
        log_entry["data"][field] = [str(entry) for entry in log_entry["data"][field]]

    print(log_entry, indata)
    for field in indata["collection"]:
        assert log_entry["data"][field] == indata["collection"][field]


def test_add_collection_bad():
    """
    Perform bad add collection attempts.

    * no {collection: {...} }
    * empty title
    * no data (no collection)
    * no data
    * list instead of object
    * incorrect field name
    * incorrect editor uuid
    * attempt to set ``_id``
    * bad dataset uuid
    """
    indata = {"title": "a title"}
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

    indata = {"collection": {"title": ""}}
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

    indata = {"collection": {}}
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

    indata = {"collection": []}
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

    indata = {"bad_field": "content", "title": "title"}
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
        "collection": {
            "description": "Test description",
            "editors": [str(uuid.uuid4())],
            "title": "Test title",
        }
    }
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
        "collection": {
            "_id": str(uuid.uuid4()),
            "title": "Test title",
        }
    }
    response = make_request(
        session, "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    assert response.code == 403
    assert not response.data

    indata = {"collection": {"datasets": [str(uuid.uuid4())], "title": "Test title"}}
    response = make_request(
        session, "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    assert response.code == 400


def test_get_collection_permissions(mdb):
    """Test permissions for requesting a collection."""
    collection = list(mdb["collections"].aggregate([{"$sample": {"size": 1}}]))[0]

    responses = make_request_all_roles(
        f'/api/v1/collection/{collection["_id"]}', ret_json=True
    )
    for response in responses:
        assert response.code == 200


def test_get_collection(mdb):
    """
    Request multiple collections by uuid, one at a time.

    * Normal collection
    * Collection as editor; confirm that the user gets the editors field
    * Collection as DATA_MANAGEMENT; confirm that the user gets the editors field
    """
    session = requests.Session()
    for _ in range(3):
        # Get a random collection, use external data structure
        collection = list(mdb["collections"].aggregate([{"$sample": {"size": 1}}]))[0]
        utils.prepare_response(collection)
        proj_owner = mdb["users"].find_one({"_id": {"$in": collection["editors"]}})
        collection["id"] = str(collection["id"])
        collection["editors"] = [str(entry) for entry in collection["editors"]]
        collection["datasets"] = [str(entry) for entry in collection["datasets"]]

        as_user(session, USERS["base"])

        response = make_request(session, f'/api/v1/collection/{collection["id"]}')
        assert response.code == 200
        for field in collection:
            if field == "datasets":
                for i, ds_uuid in enumerate(collection[field]):
                    assert ds_uuid == response.data["collection"][field][i]["id"]
            elif field == "editors":
                continue
            else:
                assert collection[field] == response.data["collection"][field]

        as_user(session, proj_owner["auth_ids"][0])
        response = make_request(session, f'/api/v1/collection/{collection["id"]}')
        assert response.code == 200
        for field in collection:
            if field in ("datasets", "editors"):
                entries = [entry["id"] for entry in response.data["collection"][field]]
                assert len(collection[field]) == len(entries)
                for i, ds_uuid in enumerate(collection[field]):
                    assert ds_uuid in entries
            else:
                assert collection[field] == response.data["collection"][field]

        as_user(session, USERS["root"])
        response = make_request(session, f'/api/v1/collection/{collection["id"]}')
        assert response.code == 200
        for field in collection:
            if field in ("datasets", "editors"):
                entries = [entry["id"] for entry in response.data["collection"][field]]
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
    Confirm that collection deletions work as intended.
    
    Checks:
    * DATA_MANAGEMENT can delete any entry.
    * Users in editors with DATA_EDIT can delete the entry.
    * No other users can delete entries.
    """
    session = requests.Session()
    collections = [entry["_id"] for entry in mdb["collections"].find({"tags": "testing"})]
    collections.append(helpers.add_collection())
    print(collections)
    helpers.as_user(session, USERS["data"])
    for coll_id in collections:
        print(coll_id)
        response = make_request(
            session, f'/api/v1/collection/{coll_id}', method="DELETE"
        )
        assert response.code == 200
        assert not response.data
        assert not mdb["collections"].find_one({"_id": coll_id})

    coll_id = helpers.add_collection()
    for role in USERS:
        helpers.as_user(session, USERS[role])
        if role in ("data", "root", "edit"):
            continue
        response = helpers.make_request(
            session, f'/api/v1/collection/{coll_id}', method="DELETE"
        )
        if role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data
        assert mdb["collections"].find_one({"_id": coll_id})

    helpers.as_user(session, USERS["data"])
    response = make_request(
        session, f'/api/v1/collection/{coll_id}', method="DELETE"
    )
    assert response.code == 200
    assert not response.data
    assert not mdb["collections"].find_one({"_id": coll_id})


def test_delete_collection_bad():
    """Attempt bad collection delete requests."""
    session = requests.Session()

    as_user(session, USERS["base"])
    for _ in range(2):
        response = make_request(
            session, f"/api/v1/collection/{random_string()}", method="DELETE"
        )
    assert response.code == 403
    assert not response.data

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
        assert response.data["data_type"] == "collection"
        assert response.data["entry_id"] == str(collection["_id"])
        assert len(response.data["logs"]) == len(logs)
        assert response.code == 200
