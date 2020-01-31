"""Tests for permission levels."""

import json

import helpers

# pylint: disable=redefined-outer-name


def test_base():
    """Request target with no permission requirements."""
    responses = helpers.make_request_all_roles('/api/developer/hello')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [{'test': "success"}]*4


def test_login_requirement():
    """Request target with no login requirement."""
    responses = helpers.make_request_all_roles('/api/developer/loginhello')
    assert [response[1] for response in responses] == [401, 200, 200, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [None,
                                           {'test': "success"},
                                           {'test': "success"},
                                           {'test': "success"}]


def test_steward_requirement():
    """Request target with no login requirement."""
    responses = helpers.make_request_all_roles('/api/developer/stewardhello')
    assert [response[1] for response in responses] == [401, 401, 200, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [None,
                                           None,
                                           {'test': "success"},
                                           {'test': "success"}]


def test_admin_requirement():
    """Request target with no login requirement."""
    responses = helpers.make_request_all_roles('/api/developer/adminhello')
    assert [response[1] for response in responses] == [401, 401, 401, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [None,
                                           None,
                                           None,
                                           {'test': "success"}]


def test_csrf():
    """
    Add a default dataset using .post(dataset/add) and confirm that CSRF works correctly.

    Should require at least Steward.
    """
    for method in ('POST', 'PUT', 'DELETE'):
        responses = helpers.make_request_all_roles('/api/developer/csrftest',
                                                   method=method, set_csrf=False)
        assert [response[1] for response in responses] == [400, 400, 400, 400]
        assert [json.loads(response[0]) if response[0] else None
                for response in responses] == [None,
                                               None,
                                               None,
                                               None]

        responses = helpers.make_request_all_roles('/api/developer/csrftest', method=method)
        assert [response[1] for response in responses] == [400, 200, 200, 200]
        assert [json.loads(response[0]) if response[0] else None
                for response in responses] == [None,
                                               {'test': 'success'},
                                               {'test': 'success'},
                                               {'test': 'success'}]
