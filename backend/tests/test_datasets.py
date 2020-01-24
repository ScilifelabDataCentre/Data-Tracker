"""Tests for dataset requests."""
import json
import time
import uuid
import requests

from helpers import make_request, as_user, make_request_all_roles, dataset_for_tests, USERS, random_string, parse_time
# pylint: disable=redefined-outer-name

def test_list_datasets():
    """
    Request a list of all datasets.

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles('/api/dataset/all')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    for response in responses:
        assert len(json.loads(response[0])['datasets']) == 500


def test_random_dataset():
    """Request a random dataset."""
    responses = make_request_all_roles('/api/dataset/random')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    for response in responses:
        assert len(json.loads(response[0])['datasets']) == 1


def test_random_datasets():
    """Request random datasets."""
    session = requests.Session()
    as_user(session, USERS['user'])
    for i in (1, 5, 0):
        response = make_request(session, f'/api/dataset/random/{i}')
        assert response[1] == 200
        assert len(response[0]['datasets']) == i

    response = make_request(session, '/api/dataset/random/-1')
    assert response[1] == 404
    assert not response[0]


def test_get_dataset_get_permissions():
    """Test permissions for requesting a dataset."""
    session = requests.Session()
    orig = make_request(session, '/api/dataset/random')[0]['datasets'][0]
    responses = make_request_all_roles(f'/api/dataset/{orig["uuid"]}')
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
        orig = make_request(session, '/api/dataset/random')[0]['datasets'][0]
        response = make_request(session, f'/api/dataset/{orig["uuid"]}')
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
        datasets = []
        while not datasets:
            orig = make_request(session, '/api/project/random')[0]['projects'][0]
            datasets = orig['datasets']
        ds_uuid = datasets[0]
        response = make_request(session, f'/api/dataset/{ds_uuid}')
        assert response[1] == 200
        assert orig['uuid'] in [proj['uuid'] for proj in response[0]['dataset']['projects']]


def test_get_dataset_bad():
    """
    Request datasets using bad identifiers.

    All are expected to return 404.
    """
    session = requests.Session()
    for _ in range(10):
        response = make_request(session, f'/api/dataset/{uuid.uuid4().hex}')
        assert response == (None, 404)

    for _ in range(10):
        response = make_request(session, f'/api/dataset/{random_string()}')
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
    
    responses = make_request_all_roles('/api/dataset/add')
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
    responses = make_request_all_roles('/api/dataset/add',
                                               method='POST',
                                               data={'dmp': 'http://test'})
    assert [response[1] for response in responses] == [400, 401, 200, 200]
    for response in responses:
        if response[1] == 200:
            data = json.loads(response[0])
            assert 'uuid' in data
            req = make_request(session, f'/api/dataset/{data["uuid"]}')
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
    responses = make_request_all_roles('/api/dataset/add',
                                               method='POST',
                                               data=indata)
    assert [response[1] for response in responses] == [400, 401, 200, 200]
    for response in responses:
        if response[1] == 200:
            data = json.loads(response[0])
            assert 'uuid' in data
            req = make_request(session, f'/api/dataset/{data["uuid"]}')
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
    as_user(session, USERS['steward'])
    indata['projects'] = [ds['uuid']
                          for ds in make_request(session,
                                                         '/api/project/random/5')[0]['projects']]
    ins_request = make_request(session,
                                       '/api/dataset/add',
                                       data=indata, method='POST')
    assert ins_request[1] == 200
    print(indata['projects'])
    print(ins_request)
    for proj_uuid in indata['projects']:
        find_request = make_request(session,
                                            f'/api/project/{proj_uuid}')
        print(find_request)
        assert ins_request[0]['uuid'] in find_request[0]['project']['datasets']
    

def test_add_bad_fields():
    """Attempt to add datasets with e.g. forbidden fields."""
    session = requests.Session()
    as_user(session, USERS['steward'])
    indata = {'dmp': 'http://test',
              'uuid': 'asd'}
    response = make_request(session,
                                    '/api/dataset/add',
                                    method='POST',
                                    data=indata)
    assert response == (None, 400)

    indata = {'dmp': 'http://test',
              'timestamp': 'asd'}
    response = make_request(session,
                                    '/api/dataset/add',
                                    method='POST',
                                    data=indata)
    assert response == (None, 400)

    indata = {'dmp': 'http://test',
              'identifier': 'asd'}
    response = make_request(session,
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
    response = make_request(session, '/api/developer/test_datasets')
    uuids = [ds['uuid'] for ds in response[0]['datasets']]

    i_user = 0
    i_uuid = 0
    users = tuple(USERS.values())
    while i_uuid < len(uuids):
        as_user(session, users[i_user])

        response = make_request(session,
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

        response = make_request(session,
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


def test_delete_ref_in_projects():
    """
    Ensure that the references to the datasets are destroyed in the projects

    Should require at least Steward.
    """
    indata = {'creator': 'Test facility',
              'data_urls': [{'description': 'Test description', 'url': 'http://test_url'}],
              'description': 'Test description',
              'dmp': 'http://test',
              'publications': ['Title. Journal: year'],
              'title': 'Test title'}

    session = requests.Session()
    as_user(session, USERS['steward'])
    indata['projects'] = [ds['uuid']
                          for ds in make_request(session,
                                                         '/api/project/random/5')[0]['projects']]
    ins_request = make_request(session,
                                       '/api/dataset/add',
                                       data=indata, method='POST')

    ds_uuid = ins_request[0]['uuid']
    response = make_request(session,
                                    f'/api/dataset/{ds_uuid}',
                                    method='DELETE')
    assert response == (None, 200)
    for proj in indata['projects']:
        response = make_request(session,
                                        f'/api/project/{proj}')
        assert ds_uuid not in response[0]['project']['datasets']


def test_delete_bad():
    """
    Bad deletion requests.

    Should require at least Steward.
    """
    session = requests.Session()
    as_user(session, USERS['steward'])
    for _ in range(3):
        ds_uuid = random_string()
        response = make_request(session,
                                f'/api/dataset/{ds_uuid}',
                                method='DELETE')
        assert response == (None, 404)
        ds_uuid = uuid.uuid4().hex
        response = make_request(session,
                                f'/api/dataset/{ds_uuid}',
                                method='DELETE')
        assert response == (None, 404)


def test_update_permissions(dataset_for_tests):
    """
    Test the permissions for the request.

    Should require at least Steward or being the owner of the dataset.
    """
    ds_uuid = dataset_for_tests
    indata = {'title': 'Updated title'}
    responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PUT', data=indata)
    assert [response[1] for response in responses] == [400, 401, 200, 200]
    assert [response[0] for response in responses] == [None]*4

    session = requests.Session()
    project = {'datasets': []}
    print(project)
    print(project.keys())
    while not project['datasets']:
        proj_response = make_request(session, f'/api/project/random')
        assert proj_response[1] == 200
        project = proj_response[0]['projects'][0]
        print(project)
    owner = project['owner']
    uuid = project['datasets'][0]
    as_user(session, owner)
    ds_response = make_request(session, f'/api/dataset/{uuid}',
                               method='PUT', data=indata)
    assert ds_response == (None, 200)


def test_update_empty(dataset_for_tests):
    """
    Confirm response 400 to an empty update request

    Should require at least Steward or being the owner of the dataset.
    """
    ds_uuid = dataset_for_tests
    responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PUT')
    assert [response[1] for response in responses] == [400, 401, 400, 400]
    assert [response[0] for response in responses] == [None]*4


def test_update(dataset_for_tests):
    """
    Update a dataset multiple times. Confirm that the update is done correctly.

    Should require at least Steward.
    """
    indata = {'creator': 'Test2 facility',
              'data_urls': [{'description': 'Test2 description', 'url': 'http://test2_url'}],
              'description': 'Test2 description',
              'dmp': 'http://test',
              'publications': ['Title. Journal: year'],
              'title': 'Test2 title'}

    session = requests.Session()
    as_user(session, USERS['steward'])

    ds_uuid = dataset_for_tests
    responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PUT', data=indata)
    assert [response[1] for response in responses] == [400, 401, 200, 200]
    assert [response[0] for response in responses] == [None]*4
    data = make_request(session, f'/api/dataset/{ds_uuid}')[0]['dataset']
    for field in indata:
        if field == 'data_urls':
            assert data['dataUrls'] == indata['data_urls']
        else:
            assert data[field] == indata[field]

    new_title = random_string()
    time.sleep(1)  # make sure that timestamp will differ
    responses = make_request(session, f'/api/dataset/{ds_uuid}',
                             method='PUT', data={'title': new_title})
    new_data = make_request(session, f'/api/dataset/{ds_uuid}')[0]['dataset']
    for field in new_data:
        if field == 'title':
            assert new_data[field] == new_title
        elif field == 'timestamp':
            new_time = parse_time(new_data[field])
            old_time = parse_time(data[field])
            assert (new_time-old_time).total_seconds() > 0
        else:
            assert new_data[field] == data[field]


def test_update_as_owner():
    """
    Add, update, and delete some datasets.

    The current user is the owner.
    """
    pass


def test_update_bad():
    """
    Confirm that bad requests will be rejected.

    Should require at least Steward.
    """
    for _ in range(3):
        ds_uuid = random_string()
        indata = {'title': 'Updated title'}
        responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PUT', data=indata)
        assert [response[1] for response in responses] == [400, 401, 404, 404]
        assert [response[0] for response in responses] == [None]*4

        ds_uuid = uuid.uuid4().hex
        responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PUT', data=indata)
        assert [response[1] for response in responses] == [400, 401, 404, 404]
        assert [response[0] for response in responses] == [None]*4

    session = requests.Session()
    as_user(session, USERS['steward'])
