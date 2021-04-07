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
