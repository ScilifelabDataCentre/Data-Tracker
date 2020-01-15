"""Tests for permission levels."""

import json
import requests

import helpers

# pylint: disable=redefined-outer-name


def test_dataset_add_get():
    """
    Request target with no permission requirements
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
