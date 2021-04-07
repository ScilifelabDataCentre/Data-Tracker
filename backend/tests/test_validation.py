"""Tests for validation functions."""
import uuid

import pytest

from helpers import mdb
import validate


def test_validate_affiliation():
    """Confirm that only valid strings are accepted."""
    validator = validate.VALIDATION_MAPPER["affiliation"]
    assert validator("Test")
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
    test_users = [str(entry['_id']) for entry in mdb["users"].aggregate([{"$sample": {"size": 5}}])]
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
    test_datasets = [str(entry['_id']) for entry in mdb["datasets"].aggregate([{"$sample": {"size": 5}}])]
    assert validator(test_datasets, db=mdb)
    assert validator(test_datasets[:1], db=mdb)
    with pytest.raises(ValueError):
        validator(test_datasets[0], db=mdb)
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


def test_validate_description():
    """Confirm that only valid strings are accepted."""
    validator = validate.VALIDATION_MAPPER["description"]
    assert validator("Test")
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
    test_users = [str(entry['_id']) for entry in mdb["users"].aggregate([{"$sample": {"size": 5}}])]
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


def test_validate_email(mdb):
    """Confirm that "only" valid emails are accepted."""
    validator = validate.VALIDATION_MAPPER["email"]
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
    test_users = [str(entry['_id']) for entry in mdb["users"].aggregate([{"$sample": {"size": 5}}])]
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


def test_validate_name():
    """Confirm that only valid strings are accepted."""
    validator = validate.VALIDATION_MAPPER["name"]
    assert validator("Test")
    assert validator("Test Name")
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
