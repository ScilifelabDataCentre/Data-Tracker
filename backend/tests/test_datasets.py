"""Tests for dataset requests."""

import json
import uuid
import requests

import helpers

# pylint: disable=redefined-outer-name

def test_list_datasets():
    """
    Request a list of all datasets.

    Should also test e.g. pagination once implemented.
    """
    responses = helpers.make_request_all_roles('/api/dataset/all')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    for response in responses:
        assert len(json.loads(response[0])['datasets']) == 500


def test_random_dataset():
    """Request a random dataset."""
    responses = helpers.make_request_all_roles('/api/dataset/random')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    for response in responses:
        assert len(json.loads(response[0])['datasets']) == 1


def test_random_datasets():
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


def test_get_dataset():
    """
    Request multiple datasets by uuid, one at a time.

    Datasets are choosen randomly using /api/dataset/random.
    """
    session = requests.Session()
    for _ in range(10):
        orig = helpers.make_request(session, '/api/dataset/random')[0]['datasets'][0]
        response = helpers.make_request(session, f'/api/dataset/{orig["uuid"]}')
        assert response[1] == 200
        requested = response[0]['dataset']
        assert orig == requested


def test_get_dataset_projects_field():
    """
    Request multiple datasets by uuid, one at a time.
    
    Make sure that the projects field contains the correct projects.

    Choose random projects, look up the datasets that should contain the project uuids.
    Projects are choosen randomly using /api/project/random.
    """
    session = requests.Session()
    for _ in range(10):
        orig = helpers.make_request(session, '/api/project/random')[0]['projects'][0]
        ds_uuid = orig['datasets'][0]
        response = helpers.make_request(session, f'/api/dataset/{ds_uuid}')
        assert response[1] == 200
        assert orig['uuid'] in response[0]['dataset']['projects']


def test_get_dataset_bad():
    """
    Request datasets using bad identifiers.

    All are expected to return 404.
    """
    session = requests.Session()
    for _ in range(10):
        response = helpers.make_request(session, f'/api/dataset/{uuid.uuid4().hex}')
        assert response == (None, 404)

    for _ in range(10):
        response = helpers.make_request(session, f'/api/dataset/{helpers.random_string()}')
        assert response == (None, 404)


def test_add_get():
    """
    Request data structure for .get(dataset/add).

    Should require at least Steward.
    """
    expected_success = {'creator': '',
                        'dataUrls': [],
                        'description': '',
                        'dmp': '',
                        'projects': [],
                        'publications': [],
                        'title': ''}
    
    responses = helpers.make_request_all_roles('/api/dataset/add')
    assert [response[1] for response in responses] == [401, 401, 200, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [None,
                                           None,
                                           expected_success,
                                           expected_success]


def test_add_permissions():
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


def test_add_all_fields():
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


def test_add_projects():
    """Add a new dataset with connected projects."""
    indata = {'creator': 'Test facility',
              'data_urls': [{'description': 'Test description', 'url': 'http://test_url'}],
              'description': 'Test description',
              'dmp': 'http://test',
              'publications': ['Title. Journal: year'],
              'title': 'Test title'}

    session = requests.Session()
    helpers.as_user(session, helpers.USERS['steward'])
    indata['projects'] = [ds['uuid']
                          for ds in helpers.make_request(session,
                                                         '/api/project/random/5')[0]['projects']]
    ins_request = helpers.make_request(session,
                                       '/api/dataset/add',
                                       data=indata, method='POST')
    assert ins_request[1] == 200
    print(indata['projects'])
    print(ins_request)
    for proj_uuid in indata['projects']:
        find_request = helpers.make_request(session,
                                            f'/api/project/{proj_uuid}')
        print(find_request)
        assert ins_request[0]['uuid'] in find_request[0]['project']['datasets']

    

def test_add_bad_fields():
    """Attempt to add datasets with e.g. forbidden fields."""
    session = requests.Session()
    helpers.as_user(session, helpers.USERS['steward'])
    indata = {'dmp': 'http://test',
              'uuid': 'asd'}
    response = helpers.make_request(session,
                                    '/api/dataset/add',
                                    method='POST',
                                    data=indata)
    assert response == (None, 400)

    indata = {'dmp': 'http://test',
              'timestamp': 'asd'}
    response = helpers.make_request(session,
                                    '/api/dataset/add',
                                    method='POST',
                                    data=indata)
    assert response == (None, 400)

    indata = {'dmp': 'http://test',
              'identifier': 'asd'}
    response = helpers.make_request(session,
                                    '/api/dataset/add',
                                    method='POST',
                                    data=indata)
    assert response == (None, 400)


def test_delete():
    """
    Delete all datasets that were created by the add tests, one at a time.

    Should require at least Steward.
    """
    session = requests.Session()
    response = helpers.make_request(session, '/api/developer/test_datasets')
    uuids = [ds['uuid'] for ds in response[0]['datasets']]

    i_user = 0
    i_uuid = 0
    users = tuple(helpers.USERS.values())
    while i_uuid < len(uuids):
        helpers.as_user(session, users[i_user])

        response = helpers.make_request(session,
                                        f'/api/dataset/{uuids[i_uuid]}',
                                        method='DELETE')
        if i_user >= 2:
            assert response == (None, 200)
            i_uuid += 1
        elif i_user == 0:
            assert response == (None, 400)
        else:
            assert response == (None, 401)

        if i_uuid >= len(uuids):
            break

        response = helpers.make_request(session,
                                        f'/api/dataset/{uuids[i_uuid]}/delete',
                                        method='POST')
        if i_user >= 2:
            assert response == (None, 200)
            i_uuid += 1
        elif i_user == 0:
            assert response == (None, 400)
        else:
            assert response == (None, 401)
        i_user = (i_user+1) % 4


def test_delete_bad():
    """
    Delete all datasets that were created by the add tests, one at a time.

    Should require at least Steward.
    """
    session = requests.Session()
    response = helpers.make_request(session, '/api/developer/test_datasets')
    uuids = [ds['uuid'] for ds in response[0]['datasets']]

    i_user = 0
    i_uuid = 0
    users = tuple(helpers.USERS.values())
    while i_uuid < len(uuids):
        helpers.as_user(session, users[i_user])

        response = helpers.make_request(session,
                                        f'/api/dataset/{uuids[i_uuid]}',
                                        method='DELETE')
        if i_user >= 2:
            assert response == (None, 200)
            i_uuid += 1
        elif i_user == 0:
            assert response == (None, 400)
        else:
            assert response == (None, 401)

        if i_uuid >= len(uuids):
            break

        response = helpers.make_request(session,
                                        f'/api/dataset/{uuids[i_uuid]}/delete',
                                        method='POST')
        if i_user >= 2:
            assert response == (None, 200)
            i_uuid += 1
        elif i_user == 0:
            assert response == (None, 400)
        else:
            assert response == (None, 401)
        i_user = (i_user+1) % 4


def test_update_permissions():
    pass
