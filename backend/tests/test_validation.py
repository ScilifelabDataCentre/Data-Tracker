"""Tests for validation functions."""
import uuid

import pytest

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
    """Confirm that only valid strings are accepted."""
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
