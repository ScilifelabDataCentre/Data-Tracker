"""Tests for validation functions."""
import uuid

import pytest

from helpers import mdb
import validate


def test_validate_affiliation():
    """Confirm that only valid strings are accepted."""
    validator = validate.VALIDATION_MAPPER["affiliation"]

    assert validator("Test")
    assert validator("")

    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator(["asd"])
    with pytest.raises(ValueError):
        validator(("asd",))
    with pytest.raises(ValueError):
        validator(4.5)


def test_validate_auth_ids():
    """Confirm that only valid lists of strings are accepted."""
    validator = validate.VALIDATION_MAPPER["auth_ids"]

    assert validator([])
    assert validator(["Test"])
    assert validator(["Test", "Test 2"])

    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator("asd")
    with pytest.raises(ValueError):
        validator([1, 2, 3, 4])
    with pytest.raises(ValueError):
        validator(4.5)


def test_validate_authors(mdb):
    """Confirm that only valid users are accepted."""
    validator = validate.VALIDATION_MAPPER["authors"]
    test_users = [
        str(entry["_id"])
        for entry in mdb["users"].aggregate([{"$sample": {"size": 5}}])
    ]

    assert validator([], db=mdb)
    assert validator(test_users, db=mdb)
    assert validator(test_users[:1], db=mdb)

    with pytest.raises(ValueError):
        validator(test_users[0], db=mdb)
    with pytest.raises(ValueError):
        validator([str(uuid.uuid4()) for _ in range(4)], db=mdb)
    with pytest.raises(ValueError):
        validator(5, db=mdb)
    with pytest.raises(ValueError):
        validator("asd", db=mdb)
    with pytest.raises(ValueError):
        validator([1, 2, 3, 4], db=mdb)
    with pytest.raises(ValueError):
        validator(4.5, db=mdb)


def test_validate_contact():
    """Confirm that only valid strings are accepted."""
    validator = validate.VALIDATION_MAPPER["contact"]

    assert validator("Test")
    assert validator("")

    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator(["asd"])
    with pytest.raises(ValueError):
        validator(("asd",))
    with pytest.raises(ValueError):
        validator(4.5)


def test_validate_datasets(mdb):
    """Confirm that only valid users are accepted."""
    validator = validate.VALIDATION_MAPPER["datasets"]
    test_datasets = [
        str(entry["_id"])
        for entry in mdb["datasets"].aggregate([{"$sample": {"size": 5}}])
    ]

    assert validator([], db=mdb)
    assert validator(test_datasets, db=mdb)
    assert validator(test_datasets[:1], db=mdb)

    with pytest.raises(ValueError):
        validator(test_datasets[0], db=mdb)
    with pytest.raises(ValueError):
        validator([str(uuid.uuid4()) for _ in range(4)], db=mdb)
    with pytest.raises(ValueError):
        validator(["not_an_uuid"], db=mdb)
    with pytest.raises(ValueError):
        validator(5, db=mdb)
    with pytest.raises(ValueError):
        validator("asd", db=mdb)
    with pytest.raises(ValueError):
        validator([1, 2, 3, 4], db=mdb)
    with pytest.raises(ValueError):
        validator(4.5, db=mdb)


def test_validate_description():
    """Confirm that only valid strings are accepted."""
    validator = validate.VALIDATION_MAPPER["description"]

    assert validator("Test")
    assert validator("")

    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator(["asd"])
    with pytest.raises(ValueError):
        validator(("asd",))
    with pytest.raises(ValueError):
        validator(4.5)


def test_validate_editors(mdb):
    """Confirm that only valid users are accepted."""
    validator = validate.VALIDATION_MAPPER["editors"]
    test_users = [
        str(entry["_id"])
        for entry in mdb["users"].aggregate([{"$sample": {"size": 5}}])
    ]

    assert validator(test_users, db=mdb)
    assert validator(test_users[:1], db=mdb)

    with pytest.raises(ValueError):
        validator(test_users[0], db=mdb)
    with pytest.raises(ValueError):
        validator([str(uuid.uuid4()) for _ in range(4)], db=mdb)
    with pytest.raises(ValueError):
        validator(["invalid_uuid"], db=mdb)
    with pytest.raises(ValueError):
        validator(5, db=mdb)
    with pytest.raises(ValueError):
        validator("asd", db=mdb)
    with pytest.raises(ValueError):
        validator([1, 2, 3, 4], db=mdb)
    with pytest.raises(ValueError):
        validator(4.5, db=mdb)


def test_validate_email(mdb):
    """Confirm that "only" valid emails are accepted."""
    validator = validate.VALIDATION_MAPPER["email"]

    assert validator("")
    assert validator("test@example.com")
    assert validator("test.name@sub.example.com")

    with pytest.raises(ValueError):
        validator("test@localhost")
    with pytest.raises(ValueError):
        validator("test@localhost@localhost.com")
    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator("asd")
    with pytest.raises(ValueError):
        validator([1, 2, 3, 4])
    with pytest.raises(ValueError):
        validator(4.5)


def test_validate_generators(mdb):
    """Confirm that only valid users are accepted."""
    validator = validate.VALIDATION_MAPPER["editors"]
    test_users = [
        str(entry["_id"])
        for entry in mdb["users"].aggregate([{"$sample": {"size": 5}}])
    ]

    assert validator([], db=mdb)
    assert validator(test_users, db=mdb)
    assert validator(test_users[:1], db=mdb)

    with pytest.raises(ValueError):
        validator(test_users[0], db=mdb)
    with pytest.raises(ValueError):
        validator([str(uuid.uuid4()) for _ in range(4)], db=mdb)
    with pytest.raises(ValueError):
        validator(["invalid_uuid"], db=mdb)
    with pytest.raises(ValueError):
        validator(5, db=mdb)
    with pytest.raises(ValueError):
        validator("asd", db=mdb)
    with pytest.raises(ValueError):
        validator([1, 2, 3, 4], db=mdb)
    with pytest.raises(ValueError):
        validator(4.5, db=mdb)


def test_validate_name():
    """Confirm that only valid strings are accepted."""
    validator = validate.VALIDATION_MAPPER["name"]

    assert validator("Test")
    assert validator("Test Name")

    with pytest.raises(ValueError):
        assert validator("")
    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator(["asd"])
    with pytest.raises(ValueError):
        validator(("asd",))
    with pytest.raises(ValueError):
        validator(4.5)


def test_validate_orcid():
    """Confirm that only valid orcids are accepted."""
    validator = validate.VALIDATION_MAPPER["orcid"]
    assert validator("0123-4567-8901-2345")
    assert validator("9999-9999-9999-9999")
    with pytest.raises(ValueError):
        validator({})
    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator(["asd"])
    with pytest.raises(ValueError):
        validator(("asd",))
    with pytest.raises(ValueError):
        validator(4.5)
    with pytest.raises(ValueError):
        validator("999F-9999-9999-9999")
    with pytest.raises(ValueError):
        validator("1234-")
    with pytest.raises(ValueError):
        validator("1234-6789")


def test_validate_organisation(mdb):
    """Confirm that only valid users are accepted."""
    validator = validate.VALIDATION_MAPPER["organisation"]
    test_users = [
        str(entry["_id"])
        for entry in mdb["users"].aggregate([{"$sample": {"size": 5}}])
    ]

    assert validator("", db=mdb)
    assert validator(test_users[0], db=mdb)
    assert validator(test_users[4], db=mdb)

    with pytest.raises(ValueError):
        validator(test_users, db=mdb)
    with pytest.raises(ValueError):
        validator(test_users[:1], db=mdb)
    with pytest.raises(ValueError):
        validator([str(uuid.uuid4()) for _ in range(4)], db=mdb)
    with pytest.raises(ValueError):
        validator(str(uuid.uuid4()), db=mdb)
    with pytest.raises(ValueError):
        validator(5, db=mdb)
    with pytest.raises(ValueError):
        validator("asd", db=mdb)
    with pytest.raises(ValueError):
        validator([1, 2, 3, 4], db=mdb)
    with pytest.raises(ValueError):
        validator(4.5, db=mdb)


def test_validate_permissions():
    """Confirm that only valid permission lists are accepted."""
    validator = validate.VALIDATION_MAPPER["permissions"]

    assert validator(["DATA_EDIT"])
    assert validator(["DATA_EDIT", "USER_MANAGEMENT"])
    assert validator([])

    with pytest.raises(ValueError):
        validator(["DATA_EDIT", "USER_MANAGEMENT", "DATA_EDIT"])
    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator([1, 2, 3])
    with pytest.raises(ValueError):
        validator(["DATA_EDIT", 2, 3])
    with pytest.raises(ValueError):
        validator("DATA_EDIT")
    with pytest.raises(ValueError):
        validator({})
    with pytest.raises(ValueError):
        validator(["BAD_PERMISSION"])
    with pytest.raises(ValueError):
        validator(("DATA_EDIT",))
    with pytest.raises(ValueError):
        validator(4.5)


def test_validate_properties():
    """Confirm that only valid key:value pairs are accepted."""
    validator = validate.VALIDATION_MAPPER["properties"]
    assert validator({})
    assert validator({"key": "value"})
    assert validator({"long key": "long value"})
    assert validator(
        {
            "key": "value",
            "key2": "value2",
            "key3": "value3",
            "key4": "value4",
            "long key": "long value",
        }
    )
    with pytest.raises(ValueError):
        assert validator({"ke": "value"})
    with pytest.raises(ValueError):
        assert validator({"key": "va"})
    with pytest.raises(ValueError):
        assert validator({"key": " value"})
    with pytest.raises(ValueError):
        assert validator({"key": "value "})
    with pytest.raises(ValueError):
        assert validator({" key": "value"})
    with pytest.raises(ValueError):
        assert validator({"key ": "value"})
    with pytest.raises(ValueError):
        assert validator({1: "value"})
    with pytest.raises(ValueError):
        assert validator({"key": 1})
    with pytest.raises(ValueError):
        assert validator(["tag"])
    with pytest.raises(ValueError):
        assert validator("")
    with pytest.raises(ValueError):
        assert validator([])
    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator(("asd",))
    with pytest.raises(ValueError):
        validator(4.5)


def test_validate_tags():
    """Confirm that only valid tags are accepted."""
    validator = validate.VALIDATION_MAPPER["tags"]

    assert validator([])
    assert validator(["test"])
    assert validator(["test", "test2"])

    with pytest.raises(ValueError):
        assert validator({})
    with pytest.raises(ValueError):
        assert validator([""])
    with pytest.raises(ValueError):
        assert validator([" tag"])
    with pytest.raises(ValueError):
        assert validator(["tag "])
    with pytest.raises(ValueError):
        assert validator(["ta"])
    with pytest.raises(ValueError):
        assert validator([0])
    with pytest.raises(ValueError):
        assert validator([0, 1, 2, 3])
    with pytest.raises(ValueError):
        assert validator("")
    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator(("asd",))
    with pytest.raises(ValueError):
        validator(4.5)


def test_validate_title():
    """Confirm that only valid strings are accepted."""
    validator = validate.VALIDATION_MAPPER["title"]

    assert validator("Test")
    assert validator("Test With more WORdS")

    with pytest.raises(ValueError):
        assert validator("")
    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator(["asd"])
    with pytest.raises(ValueError):
        validator(("asd",))
    with pytest.raises(ValueError):
        validator(4.5)


def test_validate_url():
    """Confirm that urls start with http(s)://."""
    validator = validate.VALIDATION_MAPPER["url"]

    assert validator("")
    assert validator("https://www.example.com/folder/")
    assert validator("http://www.example.com/folder/")
    assert validator("http://localhost")

    with pytest.raises(ValueError):
        validator("RandomTexthttps://www.example.com/folder/")
    with pytest.raises(ValueError):
        validator("http://")
    with pytest.raises(ValueError):
        validator("https://")
    with pytest.raises(ValueError):
        validator("ftp://localhost")
    with pytest.raises(ValueError):
        validator("Test With more WORdS")
    with pytest.raises(ValueError):
        validator(5)
    with pytest.raises(ValueError):
        validator(["asd"])
    with pytest.raises(ValueError):
        validator(("asd",))
    with pytest.raises(ValueError):
        validator(4.5)
