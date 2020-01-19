"""Tests for dataset requests."""

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
    for response in responses:
        assert len(json.loads(response[0])['datasets']) == 500


def test_random_dataset_get():
    """Request a random dataset."""
    responses = helpers.make_request_all_roles('/api/dataset/random')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    for response in responses:
        assert len(json.loads(response[0])['datasets']) == 1


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


def test_get_dataset_get_permissions():
    """Test permissions for requesting a dataset."""
    session = requests.Session()
    orig = helpers.make_request(session, '/api/dataset/random')[0]['datasets'][0]
    responses = helpers.make_request_all_roles(f'/api/dataset/{orig["uuid"]}')
    for response in responses:
        assert json.loads(response[0])['dataset'] == orig
        assert response[1] == 200


def test_get_dataset_get():
    """
    Request multiple datasets by uuid, one at a time.

    Datasets are choosen randomly using /api/dataset/random.
    """
    session = requests.Session()
    for _ in range(10):
        orig = helpers.make_request(session, '/api/dataset/random')[0]['datasets'][0]
        requested = helpers.make_request(session, f'/api/dataset/{orig["uuid"]}')[0]['dataset']
        assert orig == requested


def test_add_get():
    """
    Request data structure for .get(dataset/add).

    Should require at least Steward.
    """
    expected_success = {'creator': '',
                        'dataUrls': [],
                        'description': '',
                        'dmp': '',
                        'publications': [],
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

    Simple data content, using {identifer: test} to tell that it was added during testing.

    Should require at least Steward.
    """
    session = requests.Session()
    responses = helpers.make_request_all_roles('/api/dataset/add',
                                               method='POST',
                                               payload={'dmp': 'http://test'})
    assert [response[1] for response in responses] == [400, 401, 200, 200]
    for response in responses:
        if response[1] == 200:
            data = json.loads(response[0])
            assert 'uuid' in data
            req = helpers.make_request(session, f'/api/dataset/{data["uuid"]}')
            assert req[0]['dataset']['dmp'] == 'http://test'
        else:
            assert response[0] is None


def test_add_post_all_fields():
    """
    Add a default dataset using .post(dataset/add).

    Should require at least Steward.
    """
    indata = {'creator': 'Test facility',
              'data_urls': [{'description': 'Test description', 'url': 'http://test_url'}],
              'description': 'Test description',
              'dmp': 'http://test',
              'publications': ['Title. Journal: year'],
              'title': 'Test title'}

    session = requests.Session()
    responses = helpers.make_request_all_roles('/api/dataset/add',
                                               method='POST',
                                               payload=indata)
    assert [response[1] for response in responses] == [400, 401, 200, 200]
    for response in responses:
        if response[1] == 200:
            data = json.loads(response[0])
            assert 'uuid' in data
            req = helpers.make_request(session, f'/api/dataset/{data["uuid"]}')
            for key in indata:
                if key != 'data_urls':
                    assert req[0]['dataset'][key] == indata[key]
                else:
                    assert req[0]['dataset']['dataUrls'] == indata[key]
        else:
            assert response[0] is None


def test_delete():
    """
    Delete all datasets that were created by the add tests, one at a time.

    Should require at least Steward.
    """
    
