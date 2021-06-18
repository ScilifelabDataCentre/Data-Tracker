"""Test functions in the utils module."""

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import

import uuid

import pytest

import helpers
import utils
from helpers import mdb


def test_is_email():
    """Test whether different inputs are considered email addresses."""
    assert utils.is_email("test@example.com")
    assert utils.is_email("test.name@sub.example.com")

    assert not utils.is_email("test@localhost")
    assert not utils.is_email("test@localhost@localhost.com")
    assert not utils.is_email(5)
    assert not utils.is_email("asd")
    assert not utils.is_email("asd")
    assert not utils.is_email([1, 2, 3, 4])
    assert not utils.is_email(4.5)


def test_secure_description():
    """Confirm that html is escaped."""
    indata = '# Title *bold* <a href="http://www.example.com">Link</a>'
    expected = "# Title *bold* &lt;a href=&quot;http://www.example.com&quot;&gt;Link&lt;/a&gt;"
    assert utils.secure_description(indata) == expected


def test_prepare_response():
    """
    Test the preparation or a json response.

    * ``_id`` to ``id``
    * ``url`` added
    """
    for indata, expected in (
        ({"key": "value"}, {"key": "value"}),
        ({"_id": "value"}, {"id": "value"}),
        ({"_id": {"_id": "value"}}, {"id": {"id": "value"}}),
    ):
        utils.prepare_response(indata)
        assert indata == expected

    indata = {"lvl1": {"lvl2": "value"}}
    url = "https://www.example.com/api/v1/stuff"
    expected = {
        "url": "https://www.example.com/api/v1/stuff",
        "lvl1": {"lvl2": "value"},
    }
    utils.prepare_response(indata, url)
    assert indata == expected

    indata = {"list": [{"_id": "value"}, {"_id": "value"}, {"_id": "value"}, {"_id": "value"}]}
    expected = {"list": [{"id": "value"}, {"id": "value"}, {"id": "value"}, {"id": "value"}]}
    utils.prepare_response(indata)
    assert indata == expected

    indata = {
        "lvl1_1": 0,
        "lvl1_2": {"lvl2": {"lvl3_1": "value", "lvl3_2": {"_id": "value"}}},
    }
    expected = {
        "lvl1_1": 0,
        "lvl1_2": {"lvl2": {"lvl3_1": "value", "lvl3_2": {"id": "value"}}},
    }
    utils.prepare_response(indata)
    assert indata == expected

    indata = {"list": ({"_id": "value"}, {"_id": "value"}, {"_id": "value"}, {"_id": "value"})}
    expected = {"list": [{"id": "value"}, {"id": "value"}, {"id": "value"}, {"id": "value"}]}
    utils.prepare_response(indata)
    assert indata == expected


def test_check_permissions():
    """
    Confirm that permissions are correctly evaluated.

    Checks:
    * User not logged in (401)
    * User lacks permission (403)
    * User has permission indirectly (part of another permission) (200)
    * User has permission (200)
    """
    assert utils.check_permissions(["DATA_EDIT"], [], False) == 401
    permissions = ["DATA_EDIT"]
    user_permissions = {}
    assert utils.check_permissions(permissions, user_permissions, True) == 403
    user_permissions = ["DATA_MANAGEMENT"]
    assert utils.check_permissions(permissions, user_permissions, True) == 200
    user_permissions = ["DATA_EDIT"]
    assert utils.check_permissions(permissions, user_permissions, True) == 200


def test_commit_to_db(mdb):
    """
    Confirm that db commits work as intended.

    Checks:
        * Add a collection.
        * Update the added collection.
        * Delete the added collection.
        * Bad operation name
        * Missing ``_id`` for update
        * Missing ``_id`` for delete
    Missing checks:
        * Failed DB commit, without logger.
        * Failed DB commit, with logger.
    """
    # add
    add_data = {"title": "Test title"}
    add_data.update(helpers.TEST_LABEL)
    add_result = utils.commit_to_db(mdb, "collections", "add", add_data)
    assert add_result.acknowledged
    added_entry = mdb["collections"].find_one({"_id": add_result.inserted_id})
    for field in add_data:
        assert added_entry[field] == add_data[field]

    # update
    update_data = {"_id": add_result.inserted_id, "title": "Test title (updated)"}
    update_result = utils.commit_to_db(mdb, "collections", "edit", data=update_data)
    assert update_result.acknowledged
    updated_entry = mdb["collections"].find_one({"_id": update_data["_id"]})
    for field in update_data:
        assert updated_entry[field] == update_data[field]

    # delete
    delete_data = {"_id": update_data["_id"]}
    delete_result = utils.commit_to_db(mdb, "collections", "delete", data=delete_data)
    assert delete_result.acknowledged
    delete_entry = mdb["collections"].find_one({"_id": delete_data["_id"]})
    assert not delete_entry

    # bad operation
    with pytest.raises(ValueError):
        utils.commit_to_db(mdb, "collections", "bad_op", data=delete_data)

    # missing _id for update
    with pytest.raises(ValueError):
        utils.commit_to_db(mdb, "collections", "edit", data={"title": "new title"})

    # missing _id for delete
    with pytest.raises(ValueError):
        utils.commit_to_db(mdb, "collections", "delete", data={"title": "new title"})


def test_get_entry(mdb):
    """
    Confirm that entries are returned if they exist.

    Checks:
    * Existing collections
    * Existing datasets
    * Existing orders
    * Existing users
    * Bad uuids
    * Bad non-uuid identifiers
    """
    for dbcollection in ("collections", "datasets", "orders", "users"):
        entries = mdb[dbcollection].aggregate([{"$sample": {"size": 2}}])
        for entry in entries:
            res = utils.get_entry(mdb, dbcollection, str(entry["_id"]))
            assert res["_id"] == entry["_id"]

    for _ in range(3):
        assert not utils.get_entry(mdb, "collections", str(uuid.uuid4()))
        assert not utils.get_entry(mdb, "collections", helpers.random_string())


def test_prepare_for_db():
    """Confirm that the data is correctly prepared."""
    expected = {
        "authors": [uuid.uuid4()],
        "datasets": [uuid.uuid4()],
        "generators": [uuid.uuid4()],
        "editors": [uuid.uuid4()],
        "description": "&lt;br /&gt;",
        "tags": ["testing"],
    }
    indata = {"description": "<br />", "tags": ["testing"]}
    for key in expected:
        if key in ("editors", "authors", "generators", "datasets"):
            indata[key] = [str(expected[key][0])]
        elif key == "organisation":
            indata[key] = str(expected[key])
    print(indata)
    assert utils.prepare_for_db(indata) == expected
