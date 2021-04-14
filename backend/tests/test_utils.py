"""Test functions in the utils module."""

import utils


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
