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


def test_add_collection_permissions():
    """
    Test permissions for adding a collection.

    * Any user with ``DATA_EDIT`` can add a collection
    """
    indata = {"collection": {"title": "Test add permissions title"}}
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
            "title": "Test add title",
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
            "description": "Test bad add description",
            "editors": [str(uuid.uuid4())],
            "title": "Test bad add title",
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
            "title": "Test bad add title",
        }
    }
    response = make_request(
        session, "/api/v1/collection", method="POST", data=indata, ret_json=True
    )
    assert response.code == 403
    assert not response.data

    indata = {
        "collection": {"datasets": [str(uuid.uuid4())], "title": "Test bad add title"}
    }
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
    Confirm that only the intended users can update collections.

    Checks:
    * DATA_MANAGEMENT can edit any collection
    * DATA_EDIT and listed in editors required
    * Listed in editors, not DATA_EDIT - forbidden
    * DATA_EDIT, not listed in editors - forbidden
    """
    session = requests.Session()

    coll_id = collection_for_tests
    helpers.as_user(session, USERS["data"])
    indata = {"collection": {"title": "Update any", "editors": helpers.users_uuids()}}
    response = helpers.make_request(
        session,
        f"/api/v1/collection/{coll_id}",
        method="PATCH",
        data=indata,
        ret_json=True,
    )
    assert response.code == 200
    assert not response.data
    new_collection = mdb["collections"].find_one({"_id": coll_id})
    assert new_collection["title"] == "Update any"
    assert [str(entry) for entry in new_collection["editors"]] == helpers.users_uuids()

    for role in USERS:
        helpers.as_user(session, USERS[role])
        indata = {"collection": {"title": f"Test title - updated by {role}"}}
        response = helpers.make_request(
            session,
            f"/api/v1/collection/{coll_id}",
            method="PATCH",
            data=indata,
            ret_json=True,
        )
        if role in ("edit", "data", "root"):
            assert response.code == 200
            assert not response.data
            new_collection = mdb["collections"].find_one({"_id": coll_id})
            assert new_collection["title"] == f"Test title - updated by {role}"
        elif role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    mdb["collections"].update_one({"_id": coll_id}, {"$set": {"editors": []}})
    print(mdb["collections"].find_one({"_id": coll_id}))

    helpers.as_user(session, USERS["edit"])
    indata = {"collection": {"title": f"Test title - updated by edit"}}
    response = helpers.make_request(
        session,
        f"/api/v1/collection/{coll_id}",
        method="PATCH",
        data=indata,
        ret_json=True,
    )
    assert response.code == 403
    assert not response.data
    new_collection = mdb["collections"].find_one({"_id": coll_id})
    assert new_collection["title"] != indata["collection"]["title"]


def test_update_collection_data(mdb, collection_for_tests):
    """
    Confirm that all fields can be updated correctly.

    Checks:
    * Make update with no content -> 200
      - Confirm that log was not created
    * Make update with all relevant fields changed -> 200
      - Confirm that log was created
    * Make sure that html in description is escaped
    """
    session = requests.Session()
    helpers.as_user(session, USERS["data"])

    coll_id = collection_for_tests
    collection = mdb["collections"].find_one({"_id": coll_id})
    collection_logs = list(
        mdb["logs"].find({"_id": coll_id, "data_type": "collection"})
    )
    indata = {"collection": {}}
    response = make_request(
        session,
        f"/api/v1/collection/{coll_id}",
        method="PATCH",
        data=indata,
        ret_json=True,
    )
    assert response.code == 200
    assert not response.data
    assert collection == mdb["collections"].find_one({"_id": coll_id})
    assert len(collection_logs) == len(
        list(mdb["logs"].find({"data._id": coll_id, "data_type": "collection"}))
    )

    random_datasets = [
        str(entry["_id"])
        for entry in mdb["datasets"].aggregate([{"$sample": {"size": 5}}])
    ]
    indata = {
        "collection": {
            "title": "Update any",
            "description": "Some text",
            "editors": helpers.users_uuids(),
            "properties": {"property1": "value"},
            "tags": ["tag1", "tag2"],
            "datasets": random_datasets,
        }
    }
    response = make_request(
        session,
        f"/api/v1/collection/{coll_id}",
        method="PATCH",
        data=indata,
        ret_json=True,
    )
    assert response.code == 200
    assert not response.data
    collection = mdb["collections"].find_one({"_id": coll_id})
    for field in indata["collection"]:
        if field in ("datasets", "editors"):
            assert indata["collection"][field] == [
                str(entry) for entry in collection[field]
            ]
        else:
            assert collection[field] == indata["collection"][field]
    assert (
        len(list(mdb["logs"].find({"data._id": coll_id, "data_type": "collection"})))
        == len(collection_logs) + 1
    )

    indata = {
        "collection": {
            "description": "<br />",
        }
    }
    response = make_request(
        session,
        f"/api/v1/collection/{coll_id}",
        method="PATCH",
        data=indata,
        ret_json=True,
    )
    assert response.code == 200
    assert not response.data
    collection = mdb["collections"].find_one({"_id": coll_id})
    assert collection["description"] == "&lt;br /&gt;"
    assert (
        len(list(mdb["logs"].find({"data._id": coll_id, "data_type": "collection"})))
        == len(collection_logs) + 2
    )


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
        "editors": [str(uuid.uuid4())],
        "title": "Test bad update title",
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
        indata = {"title": "Test bad update title"}
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

        indata = {"title": "Test bad update title"}
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
    collections = [
        entry["_id"] for entry in mdb["collections"].find({"tags": "testing"})
    ]

    collections.append(helpers.add_collection())
    helpers.as_user(session, USERS["data"])
    for coll_id in collections:
        response = make_request(
            session, f"/api/v1/collection/{coll_id}", method="DELETE"
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
            session, f"/api/v1/collection/{coll_id}", method="DELETE"
        )
        if role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data
        assert mdb["collections"].find_one({"_id": coll_id})
    helpers.as_user(session, USERS["edit"])
    response = make_request(session, f"/api/v1/collection/{coll_id}", method="DELETE")
    assert response.code == 200
    assert not response.data
    assert not mdb["collections"].find_one({"_id": coll_id})

    coll_id = helpers.add_collection()
    mdb["collections"].update_one({"_id": coll_id}, {"$set": {"editors": []}})
    for role in USERS:
        helpers.as_user(session, USERS[role])
        if role in ("data", "root"):
            continue
        response = helpers.make_request(
            session, f"/api/v1/collection/{coll_id}", method="DELETE"
        )
        if role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data
        assert mdb["collections"].find_one({"_id": coll_id})

    helpers.as_user(session, USERS["data"])
    response = make_request(session, f"/api/v1/collection/{coll_id}", method="DELETE")
    assert response.code == 200
    assert not response.data
    assert not mdb["collections"].find_one({"_id": coll_id})


def test_delete_collection_bad():
    """
    Confirm that bad deletion attempts are handled correctly.

    Checks:
    * Random string as base user -> 403
    * Random string as data user -> 404
    * Random uuid as data user -> 404
    """
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
    Confirm that collection logs can only be accessed by the intended users.

    Checks:
    * DATA_MANAGEMENT can access any log.
    * DATA_EDIT can access entries where they are editors.
    * User in editors, but not DATA_EDIT cannot access logs.
    * Other users cannot access logs.
    """
    collections = list(mdb["collections"].aggregate([{"$sample": {"size": 5}}]))
    session = requests.Session()
    helpers.as_user(session, helpers.USERS["data"])
    for collection in collections:
        response = make_request(
            session, f'/api/v1/collection/{collection["_id"]}/log', ret_json=True
        )
        assert response.code == 200
        assert "logs" in response.data

    coll_id = helpers.add_collection()
    responses = make_request_all_roles(
        f"/api/v1/collection/{coll_id}/log", ret_json=True
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 200
            assert "logs" in response.data
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    base_user = mdb["users"].find_one({"auth_ids": helpers.USERS["base"]})
    mdb["collections"].update_one(
        {"_id": coll_id}, {"$set": {"editors": [base_user["_id"]]}}
    )
    for collection in collections:
        responses = make_request_all_roles(
            f'/api/v1/collection/{collection["_id"]}/log', ret_json=True
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
