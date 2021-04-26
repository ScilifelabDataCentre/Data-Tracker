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


def test_secure_description():
    """Confirm that html is escaped."""
    indata = '# Title *bold* <a href="http://www.example.com">Link</a>'
    expected = (
        "# Title *bold* &lt;a href=&quot;http://www.example.com&quot;&gt;Link&lt;/a&gt;"
    )
    assert utils.secure_description(indata) == expected


def test_prepare_response():
    """
    Test the preparation or a json response.

    * ``_id`` to ``id``
    * ``url`` added
    """
    assert utils.prepare_response({"key": "value"}) == {"key": "value"}
    assert utils.prepare_response({"_id": "value"}) == {"id": "value"}
    assert utils.prepare_response({"_id": {"_id": "value"}}) == {"id": {"id": "value"}}
    indata = ({"lvl1": {"lvl2": "value"}}, "https://www.example.com/api/v1/stuff")
    expected = {
        "url": "https://www.example.com/api/v1/stuff",
        "lvl1": {"lvl2": "value"},
    }
    assert utils.prepare_response(*indata) == expected
    indata = {
        "list": [{"_id": "value"}, {"_id": "value"}, {"_id": "value"}, {"_id": "value"}]
    }
    expected = {
        "list": [{"id": "value"}, {"id": "value"}, {"id": "value"}, {"id": "value"}]
    }
    assert utils.prepare_response(indata) == expected
    indata = {
        "lvl1_1": 0,
        "lvl1_2": {"lvl2": {"lvl3_1": "value", "lvl3_2": {"_id": "value"}}},
    }
    expected = {
        "lvl1_1": 0,
        "lvl1_2": {"lvl2": {"lvl3_1": "value", "lvl3_2": {"id": "value"}}},
    }
    assert utils.prepare_response(indata) == expected
    indata = {
        "list": ({"_id": "value"}, {"_id": "value"}, {"_id": "value"}, {"_id": "value"})
    }
    expected = {
        "list": [{"id": "value"}, {"id": "value"}, {"id": "value"}, {"id": "value"}]
    }
    assert utils.prepare_response(indata) == expected
