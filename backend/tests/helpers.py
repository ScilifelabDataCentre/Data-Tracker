"""Helper functions for tests, including requests to e.g. change current user."""

import collections
import datetime
import json
import os
import random
import re
import string
import uuid

import pytest
import requests

import config
import structure
import utils

CURR_DIR = os.path.realpath(__file__)
SETTINGS = json.loads(open(f"{os.path.dirname(CURR_DIR)}/settings_tests.json").read())
BASE_URL = f'{SETTINGS["host"]}:{SETTINGS["port"]}'

TEST_LABEL = {"tags": ["testing"]}

USERS = {
    "no-login": None,
    "base": "base::testers",
    "edit": "edit::testers",
    "owners": "owners::testers",
    "users": "users::testers",
    "data": "data::testers",
    "root": "root::testers",
}

Response = collections.namedtuple("Response", ["data", "code", "role"], defaults=[None, None, None])

FACILITY_RE = re.compile("facility[0-9]*::local")
ORGANISATION_RE = re.compile("organisation[0-9]*::local")
USER_RE = re.compile(".*::elixir")


def db_connection():
    """Get a connection to the db as defined in the app config."""
    conf = config.init()
    client = utils.get_dbclient(conf)
    return utils.get_db(client, conf)


@pytest.fixture
def mdb():
    """Get a connection to the db as defined in the app config."""
    yield db_connection()


def as_user(session: requests.Session, auth_id: str, set_csrf: bool = True) -> int:
    """
    Set the current user to the one with the provided ``auth_id``.

    Session changed in-place.

    Args:
        session (requests.Session): The session to update.
        auth_id (str): The auth id of the user.

    Returns:
        int: Status code.
    """
    if auth_id:
        code = session.get(f"{BASE_URL}/api/v1/developer/login/{auth_id}").status_code
        assert code == 200
    else:
        code = session.get(f"{BASE_URL}/api/v1/logout").status_code
        session.get(f"{BASE_URL}/api/v1/developer/hello")  # reset cookies
    if set_csrf:
        session.headers["X-CSRF-Token"] = session.cookies.get("_csrf_token")
    return code


@pytest.fixture
def dataset_for_tests():
    """
    Add a new dataset that can be modified in tests, followed by automatic removal.

    Yields the uuid of the added dataset.
    """
    uuids = add_dataset_full()
    yield uuids[1]

    # cleanup
    delete_fixture_dataset(*uuids)


def add_dataset_full():
    """
    Add an order with a dataset.

    Returns:
        tuple: (order_uuid, dataset_uuid)
    """
    mongo_db = db_connection()
    # prepare
    order_indata = structure.order()
    order_indata.update({"description": "Added by fixture.", "title": "Test title from fixture"})
    order_indata.update(TEST_LABEL)
    edit_user = mongo_db["users"].find_one({"auth_ids": USERS["edit"]})
    order_indata["authors"] = [edit_user["_id"]]
    order_indata["editors"] = [edit_user["_id"]]
    order_indata["generators"] = [edit_user["_id"]]
    order_indata["organisation"] = edit_user["_id"]

    dataset_indata = structure.dataset()
    dataset_indata.update({"description": "Added by fixture.", "title": "Test title from fixture"})
    dataset_indata.update(TEST_LABEL)

    collection_indata = structure.collection()
    collection_indata.update(
        {
            "description": "Added by fixture.",
            "title": "Test title from fixture",
            "editors": [edit_user["_id"]],
        }
    )
    collection_indata.update(TEST_LABEL)

    mongo_db["datasets"].insert_one(dataset_indata)
    order_indata["datasets"].append(dataset_indata["_id"])
    collection_indata["datasets"].append(dataset_indata["_id"])
    mongo_db["orders"].insert_one(order_indata)
    mongo_db["collections"].insert_one(collection_indata)
    return (order_indata["_id"], dataset_indata["_id"], collection_indata["_id"])


def delete_fixture_dataset(order_uuid, dataset_uuid, project_uuid):
    """Delete an order and a dataset added by ``add_dataset()``."""
    mongo_db = db_connection()
    mongo_db["orders"].delete_one({"_id": order_uuid})
    mongo_db["datasets"].delete_one({"_id": dataset_uuid})
    mongo_db["projects"].delete_one({"_id": project_uuid})


def make_request(session, url: str, data: dict = None, method="GET", ret_json: bool = True) -> dict:
    """
    Perform a request.

    Args:
        session (requests.Session()): The session to use
        url: str: The url to get without {BASE_URL} prefix (but with leading /)
        data (dict): The payload data
        method (str): HTTP method to use
        ret_json (bool): Should json.loads(response.text) be the response?

    Returns:
        tuple: (data: dict, status_code: int)
    """
    if method == "GET":
        response = session.get(f"{BASE_URL}{url}")
    elif method == "POST":
        response = session.post(f"{BASE_URL}{url}", json=data)
    elif method == "PATCH":
        response = session.patch(
            f"{BASE_URL}{url}",
            json=data,
        )
    elif method == "PUT":
        response = session.put(f"{BASE_URL}{url}", json=data)
    elif method == "DELETE":
        response = session.delete(f"{BASE_URL}{url}")
    else:
        raise ValueError(f"Unsupported http method ({method})")

    if response.text and ret_json:
        data = json.loads(response.text)
    elif response.text:
        data = response.text
    else:
        data = None
    return Response(data=data, code=response.status_code)


def make_request_all_roles(
    url: str,
    method: str = "GET",
    data=None,
    set_csrf: bool = True,
    ret_json: bool = False,
) -> list:
    """
    Perform a query for all roles (anonymous, User, Steward, Admin).

    Args:
        url (str): the url to query

    Returns:
        list: the results of the performed queries
    """
    responses = []
    session = requests.Session()
    for user in USERS:
        as_user(session, USERS[user], set_csrf=set_csrf)
        req = make_request(session, url, data, method, ret_json)
        responses.append(Response(data=req.data, code=req.code, role=user))
    return responses


@pytest.fixture
def collection_for_tests():
    """
    Add a new collection that can be modified in tests and then removed.

    Yields the uuid of the added collection.
    """
    # prepare
    ins_id = add_collection()
    yield ins_id
    mongo_db = db_connection()
    mongo_db["collections"].delete_one({"_id": ins_id})


def add_collection(datasets: list = None) -> uuid.UUID:
    """
    Add a collection that can be used for tests.

    The "edit" user is the editor.

    Args:
      datasets (list): List of dataset uuids to use for the collection.

    Returns:
        uuid.UUID: The _id of the collection.
    """
    mongo_db = db_connection()
    indata = structure.collection()
    edit_user = mongo_db["users"].find_one({"auth_ids": USERS["edit"]})
    indata.update(
        {
            "description": "Added by fixture.",
            "title": "Test title from fixture",
            "tags": ["fromFixture", "testing"],
            "editors": [edit_user["_id"]],
            "datasets": datasets or [],
        }
    )
    indata.update(TEST_LABEL)
    mongo_db["collections"].insert_one(indata)
    return indata["_id"]


def add_order() -> uuid.UUID:
    """
    Add an order that can be used for tests.

    The "edit" user is the editor.

    Returns:
        uuid.UUID: The _id of the order.
    """
    mongo_db = db_connection()
    indata = structure.order()
    edit_user = mongo_db["users"].find_one({"auth_ids": USERS["edit"]})
    indata.update(
        {
            "description": "Added by fixture.",
            "title": "Test title from fixture",
            "tags": ["fromFixture", "testing"],
            "authors": [edit_user["_id"]],
            "generators": [edit_user["_id"]],
            "organisation": edit_user["_id"],
            "editors": [edit_user["_id"]],
        }
    )
    indata.update(TEST_LABEL)
    mongo_db["orders"].insert_one(indata)
    return indata["_id"]


def add_dataset(parent: uuid.UUID) -> uuid.UUID:
    """
    Add a dataset that can be used for tests.

    Will be conneted to the provided order. The "edit" user is the editor.

    Args:
        parent (uuid.UUID): The order to use as parent.

    Returns:
        uuid.UUID: The _id of the dataset.
    """
    mongo_db = db_connection()
    indata = structure.dataset()
    indata.update(
        {
            "description": "Added by fixture.",
            "title": "Test title from fixture",
            "tags": ["fromFixture", "testing"],
        }
    )
    indata.update(TEST_LABEL)
    mongo_db["datasets"].insert_one(indata)
    mongo_db["orders"].update_one({"_id": parent}, {"$push": {"datasets": indata["_id"]}})
    return indata["_id"]


def random_string(min_length: int = 1, max_length: int = 150):
    """
    Generate a random string.

    Args:
        min_length(int): minimum length of the generated string
        max_length(int): maximum length of the generated string

    Returns:
        str: a string of random characters

    """
    char_source = string.ascii_letters + string.digits + "-"
    length = random.randint(min_length, max_length)
    return "".join(random.choice(char_source) for _ in range(length))


def parse_time(datetime_str: str):
    """
    Parse the timestamp from a query.

    Args:
        datetime_str (str): timestamp string (Wed, 22 Jan 2020 21:07:35 GMT)
    """
    str_format = "%a, %d %b %Y %H:%M:%S %Z"
    return datetime.datetime.strptime(datetime_str, str_format)


def users_uuids():
    """
    Generate a list of the uuids of all users in ``USERS``.

    Returns:
        list: All uuids (as str) for ``USERS``.
    """
    mongo_db = db_connection()
    return [
        str(mongo_db["users"].find_one({"auth_ids": USERS[entry]})["_id"])
        for entry in USERS
        if USERS[entry]
    ]
