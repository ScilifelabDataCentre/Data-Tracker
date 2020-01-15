"""Tests for permission levels."""

import json
import requests

import helpers

# pylint: disable=redefined-outer-name


def test_base():
    """
    Request target with no permission requirements
    """
    responses = helpers.request_all_permissions('/api/developer/hello')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [{'test': "success"}]*4


def test_login_requirement():
    """
    Request target with no login requirement
    """
    responses = helpers.request_all_permissions('/api/developer/loginhello')
    assert [response[1] for response in responses] == [401, 200, 200, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [None,
                                           {'test': "success"},
                                           {'test': "success"},
                                           {'test': "success"}]


def test_steward_requirement():
    """
    Request target with no login requirement
    """
    responses = helpers.request_all_permissions('/api/developer/stewardhello')
    assert [response[1] for response in responses] == [401, 401, 200, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [None,
                                           None,
                                           {'test': "success"},
                                           {'test': "success"}]


def test_admin_requirement():
    """
    Request target with no login requirement
    """
    responses = helpers.request_all_permissions('/api/developer/adminhello')
    assert [response[1] for response in responses] == [401, 401, 401, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [None,
                                           None,
                                           None,
                                           {'test': "success"}]
