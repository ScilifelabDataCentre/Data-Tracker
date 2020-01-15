"""Tests for permission levels."""

import json
import requests

import helpers

# pylint: disable=redefined-outer-name


def test_add_get():
    """
    Request data structure for .get(dataset/add).

    Should require at least Steward.
    """
    expected_success = {'creator': '',
                        'description': '',
                        'dmp': '',
                        'identifier': '',
                        'publications': [ ],
                        'title': ''}
    
    responses = helpers.make_request_all_roles('/api/dataset/add')
    assert [response[1] for response in responses] == [401, 401, 200, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [None,
                                           None,
                                           expected_success,
                                           expected_success]


def test_add_post_permissions():
    """
    Add a default dataset using .post(dataset/add).

    Should require at least Steward.
    """
    responses = helpers.make_request_all_roles('/api/dataset/add', method='POST')
    assert [response[1] for response in responses] == [400, 401, 200, 200]
    assert [list(json.loads(response[0]).keys())[0] if response[0] else None
            for response in responses] == [None,
                                           None,
                                           'uuid',
                                           'uuid']
