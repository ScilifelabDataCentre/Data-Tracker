"""Tests for permission levels."""

import json
import requests

import helpers

# pylint: disable=redefined-outer-name


def test_list_datasets_get():
    """
    Request a list of all datasets.

    Should also test e.g. pagination once implemented.
    """
    responses = helpers.make_request_all_roles('/api/dataset/all')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    assert [len(json.loads(response[0])['datasets']) > 10 for response in responses] == [True]*4


def test_random_dataset_get():
    """Request a random dataset."""
    responses = helpers.make_request_all_roles('/api/dataset/random')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    assert [len(json.loads(response[0])['datasets']) == 1 for response in responses] == [True]*4


def test_random_datasets_get():
    """Request random datasets."""
    session = requests.Session()
    helpers.as_user(session, helpers.USERS['user'])
    for i in (1, 5, 0):
        response = helpers.make_request(session, f'/api/dataset/random/{i}')
        assert response[1] == 200
        assert len(response[0]['datasets']) == i

    response = helpers.make_request(session, '/api/dataset/random/-1')
    assert response[1] == 404
    assert not response[0]


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
