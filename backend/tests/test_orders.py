"""Tests for order requests."""
import uuid

import requests

import order
import utils

import helpers

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import
from helpers import (
    make_request,
    as_user,
    make_request_all_roles,
    USERS,
    random_string,
    TEST_LABEL,
    mdb,
    USER_RE,
)


def test_list_all_orders(mdb):
    """
    Confirm that orders are listed correctly.

    Checks:
    * DATA_MANAGEMENT lists all orders
    * DATA_EDIT gets all orders where they are editors
    * Other users get 403 or 401
    * Order should contain id, title, tags, properties
    """
    nr_orders = mdb["orders"].count_documents({})
    responses = helpers.make_request_all_roles("/api/v1/order", ret_json=True)
    for response in responses:
        if response.role in ("data", "root"):
            assert response.code == 200
            assert len(response.data["orders"]) == nr_orders
            assert set(response.data["orders"][0].keys()) == {
                "id",
                "properties",
                "tags",
                "title",
            }
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data

        elif response.role == "edit":
            assert response.code == 200
            edit_user = mdb["users"].find_one({"auth_ids": helpers.USERS["edit"]})
            edit_orders = mdb["orders"].count_documents({"editors": edit_user["_id"]})
            assert len(response.data["orders"]) == edit_orders

        else:
            assert response.code == 403
            assert not response.data

    order_id = next(mdb["orders"].aggregate([{"$sample": {"size": 1}}]))
    user_info = mdb["users"].find_one({"_id": order_id["editors"][0]})
    order_count = mdb["orders"].count_documents({"editors": user_info["_id"]})
    session = requests.Session()
    helpers.as_user(session, user_info["auth_ids"][0])
    response = helpers.make_request(session, "/api/v1/order", ret_json=True)
    assert response.code == 200
    assert len(response.data["orders"]) == order_count
    assert set(response.data["orders"][0].keys()) == {
        "id",
        "properties",
        "tags",
        "title",
    }


def test_get_order_permissions(mdb):
    """
    Confirm that only the correct users can access order information.

    Checks:
    * DATA_MANAGEMENT can access any order
    * DATA_EDIT can access orders where they are
    * Other users cannot access data
    """
    session = requests.Session()

    orders = list(
        mdb["orders"].aggregate(
            [{"$match": {"auth_ids": USER_RE}}, {"$sample": {"size": 2}}]
        )
    )
    for order in orders:
        owner = mdb["users"].find_one({"_id": order["editors"][0]})
        responses = helpers.make_request_all_roles(
            f'/api/v1/order/{order["_id"]}', ret_json=True
        )
        for response in responses:
            if response.role in ("data", "root"):
                assert response.code == 200
            elif response.role == "no-login":
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        helpers.as_user(session, owner["auth_ids"][0])
        response = make_request(session, f'/api/v1/order/{order["_id"]}')
        assert response.code == 200


def test_get_order_data(mdb):
    """
    Confirm that the retrieved data is from the correct order and contain the correct data.

    Checks:
    * Request multiple orders by uuid, one at a time.
      - Request the order and confirm that it contains the correct data.
    """
    session = requests.Session()
    as_user(session, USERS["data"])

    orders = list(mdb["orders"].aggregate([{"$sample": {"size": 3}}]))
    for order in orders:
        # to simplify comparison
        order["_id"] = str(order["_id"])
        # user entries
        for key in ("authors", "generators", "editors"):
            order[key] = utils.user_uuid_data(order[key], mdb)
        order["organisation"] = utils.user_uuid_data(order["organisation"], mdb)[0]

        for i, ds in enumerate(order["datasets"]):
            order["datasets"][i] = next(
                mdb["datasets"].aggregate(
                    [{"$match": {"_id": ds}}, {"$project": {"_id": 1, "title": 1}}]
                )
            )
            order["datasets"][i]["_id"] = str(order["datasets"][i]["_id"])

        response = make_request(session, f'/api/v1/order/{order["_id"]}')
        assert response.code == 200
        data = response.data["order"]
        assert len(order) == len(data)
        for field in order:
            if field in ("authors", "datasets", "generators", "editors"):
                assert len(order[field]) == len(data[field])
                assert set(subentry["_id"] for subentry in order[field]) == set(
                    subentry["id"] for subentry in data[field]
                )
            elif field == "_id":
                assert order["_id"] == data["id"]
            elif field == "organisation":
                assert order[field]["_id"] == data[field]["id"]
            else:
                assert order[field] == data[field]


def test_get_order_bad():
    """
    Request orders using bad identifiers.

    All are expected to return 401, 403, or 404 depending on permissions.
    """
    for _ in range(2):
        responses = make_request_all_roles(f"/api/v1/order/{uuid.uuid4()}")
        for response in responses:
            if response.role in ("edit", "data", "root"):
                assert response.code == 404
            elif response.role == "no-login":
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data

    for _ in range(2):
        responses = make_request_all_roles(f"/api/v1/order/{random_string()}")
        for response in responses:
            if response.role in ("edit", "data", "root"):
                assert response.code == 404
            elif response.role == "no-login":
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data


def test_get_order_logs_permissions(mdb):
    """
    Confirm that only the intended users can access the logs.

    Checks:
    * DATA_MANAGEMENT can access logs for any order
    * DATA_EDIT required to be in editors
    """
    order_data = mdb["orders"].aggregate([{"$sample": {"size": 1}}]).next()
    edit_user = mdb["users"].find_one({"auth_ids": USERS["edit"]})
    # in case the edit user is an editor
    mdb["orders"].update_one(
        {"_id": order_data["_id"]}, {"$pull": {"editors": edit_user["_id"]}}
    )
    responses = helpers.make_request_all_roles(
        f'/api/v1/order/{order_data["_id"]}/log', ret_json=True
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

    mdb["orders"].update_one(
        {"_id": order_data["_id"]}, {"$push": {"editors": edit_user["_id"]}}
    )
    print(mdb["orders"].find_one({"_id": order_data["_id"]}))
    print(edit_user)
    helpers.as_user(session, USERS["edit"])
    response = make_request(
        session, f'/api/v1/order/{order_data["_id"]}/log', ret_json=True
    )

    assert response.code == 200
    assert "logs" in response.data


def test_get_order_logs(mdb):
    """
    Request the logs for multiple orders.

    Confirm that the logs contain only the intended fields.
    """
    session = requests.session()
    db = mdb
    orders = db["orders"].aggregate([{"$sample": {"size": 2}}])
    for order in orders:
        logs = list(db["logs"].find({"data_type": "order", "data._id": order["_id"]}))
        as_user(session, USERS["data"])
        response = make_request(
            session, f'/api/v1/order/{order["_id"]}/log', ret_json=True
        )
        assert response.data["data_type"] == "order"
        assert response.data["entry_id"] == str(order["_id"])
        assert len(response.data["logs"]) == len(logs)
        assert response.code == 200


def test_get_order_logs_bad():
    """
    Request the logs for multiple orders.

    Confirm that bad identifiers give response 404.
    """
    session = requests.session()
    for _ in range(2):
        as_user(session, USERS["data"])
        response = make_request(
            session, f"/api/v1/order/{uuid.uuid4()}/log", ret_json=True
        )
        assert response.code == 404
        response = make_request(
            session, f"/api/v1/order/{random_string()}/log", ret_json=True
        )
        assert response.code == 404


def test_add_order_permissions():
    """
    Confirm that only the intended users can create orders.

    Checks:
    * Only users with DATA_MANAGEMENT or DATA_EDIT can create orders
    """
    indata = {"order": {"title": "Test order add title"}}
    indata["order"].update(TEST_LABEL)
    responses = make_request_all_roles(
        "/api/v1/order", method="POST", data=indata, ret_json=True
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


def test_add_order(mdb):
    """
    Confirm that orders are added correctly.

    Checks:
    * Add order as DATA_EDIT
      - Confirm that the fields are set correctly
      - No editor -> current user becomes editor
      - With editors -> current user should still become editor
    * Add order as DATA_MANAGEMENT
      - Confirm that the fields are set correctly
      - No editor -> current user becomes editor
      - With editors -> current user should not become editor
    * Confirm that description is escaped.
    """
    session = requests.Session()
    root_user = mdb["users"].find_one({"auth_ids": USERS["root"]})

    for test_user in ("edit", "data"):
        helpers.as_user(session, USERS[test_user])

        indata = {"order": {"description": "Test description", "title": "Test title"}}
        indata["order"].update(TEST_LABEL)
        current_user = mdb["users"].find_one({"auth_ids": USERS[test_user]})
        response = helpers.make_request(
            session, "/api/v1/order", method="POST", data=indata, ret_json=True
        )
        # to make comparisons shorter
        indata = indata["order"]
        assert response.code == 200
        assert "id" in response.data
        assert len(response.data["id"]) == 36
        order = mdb["orders"].find_one({"_id": uuid.UUID(response.data["id"])})
        assert order["description"] == indata["description"]
        assert order["title"] == indata["title"]
        # if editors is empty, current user should be editor
        assert current_user["_id"] in order["editors"]

        indata = {
            "order": {
                "description": "<br />",
                "authors": [str(root_user["_id"])],
                "editors": [str(root_user["_id"])],
                "generators": [str(root_user["_id"])],
                "organisation": str(root_user["_id"]),
                "title": "Test title",
            }
        }
        indata["order"].update(TEST_LABEL)

        response = helpers.make_request(
            session, "/api/v1/order", method="POST", data=indata, ret_json=True
        )
        # to make comparisons shorter
        indata = indata["order"]
        assert response.code == 200
        assert "id" in response.data
        assert len(response.data["id"]) == 36
        order = mdb["orders"].find_one({"_id": uuid.UUID(response.data["id"])})

        user_list = [root_user["_id"]]
        assert order["title"] == indata["title"]
        # confirm that description is escaped
        assert order["description"] == "&lt;br /&gt;"
        for field in ("authors", "generators"):
            assert order[field] == user_list
        if test_user == "edit":
            assert order["editors"] == user_list + [current_user["_id"]]
        elif test_user == "data":
            assert order["editors"] == user_list
        assert order["organisation"] == root_user["_id"]


def test_add_order_log(mdb):
    """
    Confirm that logs are created when orders are added.

    Checks:
    * Confirm that a log entry is created after order is added.
    """
    indata = {
        "order": {
            "description": "Test add order log description",
            "title": "Test add order log title",
        }
    }
    indata["order"].update(TEST_LABEL)

    session = requests.Session()
    helpers.as_user(session, USERS["edit"])
    response = helpers.make_request(
        session, "/api/v1/order", method="POST", data=indata, ret_json=True
    )
    assert response.code == 200
    assert "id" in response.data
    assert len(response.data["id"]) == 36
    order = mdb["orders"].find_one({"_id": uuid.UUID(response.data["id"])})
    logs = list(
        mdb["logs"].find(
            {"data_type": "order", "data._id": uuid.UUID(response.data["id"])}
        )
    )
    assert len(logs) == 1
    assert logs[0]["data"] == order
    assert logs[0]["action"] == "add"


def test_add_order_bad():
    """
    Confirm that bad order content is rejected.

    Checks:
    * Bad uuid
    * No "order" field with data
    * Attempting to set _id
    * Bad field name
    """
    indata = {
        "order": {
            "description": "Test description",
            "authors": [str(uuid.uuid4())],
            "title": "Test title",
        }
    }
    indata["order"].update(TEST_LABEL)

    responses = make_request_all_roles(
        "/api/v1/order", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 400
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"title": "Test title"}
    indata.update(TEST_LABEL)
    responses = make_request_all_roles(
        "/api/v1/order", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 400
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"order": {"_id": str(uuid.uuid4()), "title": "Test title"}}
    indata["order"].update(TEST_LABEL)
    responses = make_request_all_roles(
        "/api/v1/order", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 403
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"order": {"made_up_property": [], "title": "Test title"}}
    indata["order"].update(TEST_LABEL)
    responses = make_request_all_roles(
        "/api/v1/order", method="POST", data=indata, ret_json=True
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 400
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data


def test_update_order_permissions(mdb):
    """
    Confirm orders can only be modified by the indented users.

    Checks:
      * Order be edited by DATA_MANAGEMENT
      * Order be edited by DATA_EDIT if user is in editors
      * Order cannot be edited by DATA_EDIT if user is in editors
      * Other users cannot edit order
    """
    order_id = helpers.add_order()
    edit_user = mdb["users"].find_one({"auth_ids": USERS["edit"]})
    indata = {"order": {"title": "Test update order title"}}
    responses = helpers.make_request_all_roles(
        f"/api/v1/order/{order_id}", method="PATCH", data=indata, ret_json=True
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 200
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    mdb["orders"].update_one(
        {"_id": order_id}, {"$pull": {"editors": edit_user["_id"]}}
    )
    responses = helpers.make_request_all_roles(
        f"/api/v1/order/{order_id}", method="PATCH", data=indata, ret_json=True
    )
    for response in responses:
        if response.role in ("data", "root"):
            assert response.code == 200
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data


def test_update_order_data(mdb):
    """
    Confirm that data is updated correctly.

    Checks:
      * All fields are correctly updated
      * Confirm that description is escaped
      * DATA_MANAGEMENT can remove themselves from editors
      * DATA_EDIT cannot remove themselves from editors
      * Confirm that description is escaped
      * Confirm that a log entry is created
    """
    root_user = mdb["users"].find_one({"auth_ids": USERS["root"]})
    session = requests.Session()

    for test_user in ("edit", "data"):
        order_id = helpers.add_order()
        current_user = mdb["users"].find_one({"auth_ids": USERS[test_user]})
        helpers.as_user(session, USERS[test_user])
        indata = {
            "order": {
                "description": "<br />",
                "authors": [str(root_user["_id"])],
                "editors": [str(current_user["_id"]), str(root_user["_id"])],
                "generators": [str(root_user["_id"])],
                "organisation": str(root_user["_id"]),
                "title": "Test update order title",
                "tags": ["testing", "updated"],
            }
        }
        indata["order"].update(TEST_LABEL)

        response = helpers.make_request(
            session,
            f"/api/v1/order/{order_id}",
            method="PATCH",
            data=indata,
            ret_json=True,
        )
        # to make comparisons shorter
        indata = indata["order"]
        assert response.code == 200
        assert not response.data
        order = mdb["orders"].find_one({"_id": order_id})
        user_list = [root_user["_id"]]
        assert order["title"] == indata["title"]
        # confirm that description is escaped
        assert order["description"] == "&lt;br /&gt;"
        for field in ("authors", "generators"):
            assert order[field] == user_list
        assert order["editors"] == [current_user["_id"]] + user_list
        assert order["organisation"] == root_user["_id"]

        indata = {"order": {"editors": [str(root_user["_id"])],}}
        response = helpers.make_request(
            session,
            f"/api/v1/order/{order_id}",
            method="PATCH",
            data=indata,
            ret_json=True,
        )
        log_count = 1
        if test_user == "edit":
            assert response.code == 400
        elif test_user == "data":
            assert response.code == 200
            log_count = 2
        assert (
            len(
                list(
                    mdb["logs"].find(
                        {
                            "data._id": order_id,
                            "action": "edit",
                            "data_type": "order",
                            "user": current_user["_id"],
                        }
                    )
                )
            )
            == log_count
        )


def test_update_order_bad(mdb):
    """
    Confirm that bad data is rejected.

    Checks:
      * Bad uuid
      * No uuid list (only str)
      * No "orders" property with data
      * Bad order uuid
      * Bad order string
    """
    order_id = helpers.add_order()
    edit_user = mdb["users"].find_one({"auth_ids": USERS["edit"]})
    indata = {
        "orders": {
            "description": "Test description",
            "authors": [str(uuid.uuid4())],
            "title": "Test title",
        }
    }
    responses = make_request_all_roles(
        f"/api/v1/order/{order_id}", method="PATCH", data=indata, ret_json=True
    )
    for response in responses:
        if response.role in ("edit", "data", "root"):
            assert response.code == 400
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

        indata = {
            "description": "Test description",
            "editors": [str(edit_user["_id"])],
            "title": "Test title",
        }
        responses = make_request_all_roles(
            f"/api/v1/order/{order_id}", method="PATCH", data=indata, ret_json=True
        )
        for response in responses:
            if response.role in ("edit", "data", "root"):
                assert response.code == 400
            elif response.role == "no-login":
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

    for _ in range(2):
        indata = {"title": "Test title"}
        responses = make_request_all_roles(
            f"/api/v1/order/{uuid.uuid4()}", method="PATCH", data=indata, ret_json=True
        )
        for response in responses:
            if response.role in ("edit", "data", "root"):
                assert response.code == 404
            elif response.role == "no-login":
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        indata = {"title": "Test title"}
        responses = make_request_all_roles(
            f"/api/v1/order/{random_string}",
            method="PATCH",
            data=indata,
            ret_json=True,
        )
        for response in responses:
            if response.role in ("edit", "data", "root"):
                assert response.code == 404
            elif response.role == "no-login":
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data


def test_delete_order(mdb):
    """
    Add and delete orders.

    * Check permissions.
    * Delete orders added by the add tests.
    * Confirm that related datasets are deleted.
    * Check that logs are created correctly.
    """
    session = requests.Session()

    db = mdb

    edit_user = db["users"].find_one({"auth_ids": USERS["edit"]})

    orders = list(db["orders"].find(TEST_LABEL))
    if not orders:
        assert False
    i = 0
    while i < len(orders):
        for role in USERS:
            as_user(session, USERS[role])
            response = make_request(
                session, f'/api/v1/order/{orders[i]["_id"]}', method="DELETE"
            )
            if role in ("edit", "data", "root"):
                if role != "edit" or edit_user["_id"] in orders[i]["editors"]:
                    assert response.code == 200
                    assert not response.data
                    assert not db["orders"].find_one({"_id": orders[i]["_id"]})
                    assert db["logs"].find_one(
                        {
                            "data._id": orders[i]["_id"],
                            "action": "delete",
                            "data_type": "order",
                        }
                    )
                    for dataset_uuid in orders[i]["datasets"]:
                        assert not db["datasets"].find_one({"_id": dataset_uuid})
                        assert db["logs"].find_one(
                            {
                                "data._id": dataset_uuid,
                                "action": "delete",
                                "data_type": "dataset",
                            }
                        )
                    i += 1
                    if i >= len(orders):
                        break
                else:
                    assert response.code == 403
                    assert not response.data
            elif role == "no-login":
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

    as_user(session, USERS["edit"])
    response = make_request(
        session, "/api/v1/order", data={"title": "tmp"}, method="POST"
    )
    assert response.code == 200
    response = make_request(
        session, f'/api/v1/order/{response.data["id"]}', method="DELETE"
    )
    assert response.code == 200
    assert not response.data


def test_delete_order_bad():
    """Attempt bad order delete requests."""
    session = requests.Session()

    as_user(session, USERS["data"])
    for _ in range(2):
        response = make_request(
            session, f"/api/v1/order/{random_string()}", method="DELETE"
        )
    assert response.code == 404
    assert not response.data

    for _ in range(2):
        response = make_request(
            session, f"/api/v1/order/{uuid.uuid4()}", method="DELETE"
        )
    assert response.code == 404
    assert not response.data


def test_add_dataset_permissions(mdb):
    """
    Add a dataset using .post(addDataset).

    Confirm that permissions are handled correctly.
    """
    session = requests.Session()

    db = mdb
    orders = db["orders"].aggregate([{"$sample": {"size": 2}}])
    for order in orders:
        indata = {"title": "Test title"}
        indata.update(TEST_LABEL)

        responses = make_request_all_roles(
            f"/api/v1/order/{str(order['_id'])}/dataset",
            method="POST",
            data=indata,
            ret_json=True,
        )
        for response in responses:
            if response.role in ("data", "root"):
                assert response.code == 200
                assert "id" in response.data
                assert len(response.data["id"]) == 36
            elif response.role == "no-login":
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        # as order editor
        owner = db["users"].find_one({"_id": order["editors"][0]})
        as_user(session, owner["auth_ids"][0])
        response = make_request(
            session,
            f"/api/v1/order/{str(order['_id'])}/dataset",
            method="POST",
            data=indata,
        )
        assert response.code == 200
        assert "id" in response.data
        assert len(response.data["id"]) == 36


def test_add_dataset(mdb):
    """
    Add a dataset using POST dataset.

    Set values in all available fields.
    """
    order = next(mdb["orders"].aggregate([{"$sample": {"size": 1}}]))
    indata = {
        "title": "Test title",
        "description": "Test description",
    }
    indata.update(TEST_LABEL)

    session = requests.session()
    as_user(session, USERS["data"])

    response = make_request(
        session,
        f"/api/v1/order/{order['_id']}/dataset",
        method="POST",
        data=indata,
        ret_json=True,
    )
    assert response.code == 200
    assert "id" in response.data
    assert len(response.data["id"]) == 36
    indata.update({"_id": response.data["id"]})
    mdb_ds = mdb["datasets"].find_one({"_id": uuid.UUID(response.data["id"])})
    mdb_o = mdb["orders"].find_one({"_id": order["_id"]})
    mdb_ds["_id"] = str(mdb_ds["_id"])
    mdb_o["datasets"] = [str(ds_uuid) for ds_uuid in mdb_o["datasets"]]
    for field in indata:
        if field == "order":
            continue
        assert mdb_ds[field] == indata[field]
    assert response.data["id"] in mdb_o["datasets"]


def test_add_dataset_log(mdb):
    """
    Confirm that logs are added correctly when datasets are added.

    Check that both there is both update on order and add on dataset.
    """
    order = next(mdb["orders"].aggregate([{"$sample": {"size": 1}}]))
    indata = {"title": "Test title"}
    indata.update(TEST_LABEL)

    session = requests.session()
    as_user(session, USERS["data"])

    order_logs = list(
        mdb["logs"].find({"data_type": "order", "data._id": order["_id"]})
    )

    response = make_request(
        session,
        f"/api/v1/order/{order['_id']}/dataset",
        method="POST",
        data=indata,
        ret_json=True,
    )

    order_logs_post = list(
        mdb["logs"].find({"data_type": "order", "data._id": order["_id"]})
    )
    print(order_logs_post)
    assert len(order_logs_post) == len(order_logs) + 1
    ds_logs_post = list(
        mdb["logs"].find(
            {"data_type": "dataset", "data._id": uuid.UUID(response.data["id"])}
        )
    )
    assert len(ds_logs_post) == 1
    assert ds_logs_post[0]["action"]


def test_add_dataset_bad_fields(mdb):
    """Attempt to add datasets with e.g. forbidden fields."""
    db = mdb
    order = next(db["orders"].aggregate([{"$sample": {"size": 1}}]))
    session = requests.Session()
    as_user(session, USERS["data"])

    indata = {
        "_id": "asd",
        "title": "test title",
    }
    response = make_request(
        session, f"/api/v1/order/{order['_id']}/dataset", method="POST", data=indata
    )
    assert response.code == 403
    assert not response.data

    indata = {"timestamp": "asd", "title": "test title"}
    response = make_request(
        session, f"/api/v1/order/{order['_id']}/dataset", method="POST", data=indata
    )
    assert response.code == 400
    assert not response.data

    indata = {"extra": [{"asd": 123}], "title": "test title"}
    response = make_request(
        session, f"/api/v1/order/{order['_id']}/dataset", method="POST", data=indata
    )
    assert response.code == 400
    assert not response.data

    indata = {"links": [{"asd": 123}], "title": "test title"}
    response = make_request(
        session, f"/api/v1/order/{order['_id']}/dataset", method="POST", data=indata
    )
    assert response.code == 400
    assert not response.data

    indata = {"links": "Some text", "title": "test title"}
    response = make_request(
        session, f"/api/v1/order/{order['_id']}/dataset", method="POST", data=indata
    )
    assert response.code == 400
    assert not response.data


def test_prepare_order_response(mdb):
    """
    Confirm that the order is prepared the intended way.

    Checks:
    """
    order_id = helpers.add_order()
    dataset_id = helpers.add_dataset(order_id)
    order_data = mdb["orders"].find_one({"_id": order_id})
    user_info = {
        "_id": "3e013a6f-502c-40d7-8a09-69f96e0960e4",
        "affiliation": "Test University",
        "contact": "pub_Edit@example.com",
        "name": "Edit",
        "orcid": "1111-1111-1111-1111",
        "url": "https://www.example.com/specuser",
    }
    order.prepare_order_response(order_data, mdb)
    for field in ("editors", "authors", "generators"):
        assert order_data[field] == [user_info]
    assert order_data["datasets"] == [
        {"title": "Test title from fixture", "_id": dataset_id}
    ]
    assert order_data["organisation"] == user_info
