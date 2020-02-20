"""Tests for dataset requests."""
import json
import uuid
import requests

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import

from helpers import make_request, as_user, make_request_all_roles,\
    dataset_for_tests, USERS, random_string, parse_time, db_connection

TEST_DS_LABEL = {'description': 'Test dataset'}


def test_list_datasets():
    """
    Request a list of all datasets.

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles('/api/dataset/all', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['datasets']) == 500


def test_random_dataset():
    """Request a random dataset."""
    responses = make_request_all_roles('/api/dataset/random', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['datasets']) == 1


def test_random_datasets():
    """Request random datasets."""
    session = requests.Session()
    as_user(session, USERS['base'])
    for i in (1, 5, 0):
        response = make_request(session, f'/api/dataset/random/{i}')
        assert response.code == 200
        assert len(response.data['datasets']) == i

    response = make_request(session, '/api/dataset/random/-1')
    assert response.code == 404
    assert not response.data


def test_get_dataset_get_permissions():
    """Test permissions for requesting a dataset."""
    session = requests.Session()
    db = db_connection()
    orders = list(db['datasets'].aggregate([{'$sample': {'size': 2}}]))
    for order in orders:
        responses = make_request_all_roles(f'/api/dataset/{order["_id"]}', ret_json=True)
        for response in responses:
            assert response.data['dataset']
            assert response.code == 200


def test_get_dataset():
    """
    Request multiple datasets by uuid, one at a time.

    Datasets are choosen randomly using /api/dataset/random.
    """
    session = requests.Session()
    for _ in range(10):
        orig = make_request(session, '/api/dataset/random')[0]['datasets'][0]
        response = make_request(session, f'/api/dataset/{orig["_id"]}')
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
        assert orig['_id'] in [proj['_id'] for proj in response[0]['dataset']['projects']]


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
    expected_success = {'links': [],
                        'description': '',
                        'projects': [],
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
                                       data=TEST_DS_LABEL)
    assert [response[1] for response in responses] == [400, 401, 200, 200]
    for response in responses:
        if response[1] == 200:
            data = json.loads(response[0])
            assert '_id' in data
            req = make_request(session, f'/api/dataset/{data["_id"]}')
            assert req[0]['dataset']['description'] == TEST_DS_LABEL['description']
        else:
            assert response[0] is None


def test_add_all_fields():
    """
    Add a default dataset using .post(dataset/add).

    Should require at least Steward.
    """
    indata = {'links': [{'description': 'Test description', 'url': 'http://test_url'}],
              'title': 'Test title'}
    indata.update(TEST_DS_LABEL)

    session = requests.Session()
    responses = make_request_all_roles('/api/dataset/add',
                                       method='POST',
                                       data=indata)
    assert [response[1] for response in responses] == [400, 401, 200, 200]
    for response in responses:
        if response[1] == 200:
            data = json.loads(response[0])
            assert '_id' in data
            req = make_request(session, f'/api/dataset/{data["_id"]}')
            for key in indata:
                if key != 'links':
                    assert req[0]['dataset'][key] == indata[key]
                else:
                    assert req[0]['dataset']['links'] == indata[key]
        else:
            assert response[0] is None


def test_add_projects():
    """Add a new dataset with connected projects."""
    indata = {'links': [{'description': 'Test description', 'url': 'http://test_url'}],
              'title': 'Test title'}
    indata.update(TEST_DS_LABEL)

    session = requests.Session()
    as_user(session, USERS['steward'])
    indata['projects'] = [ds['_id']
                          for ds in make_request(session,
                                                 '/api/project/random/5')[0]['projects']]
    ins_request = make_request(session,
                               '/api/dataset/add',
                               data=indata, method='POST')
    assert ins_request[1] == 200
    for proj_uuid in indata['projects']:
        find_request = make_request(session,
                                    f'/api/project/{proj_uuid}')
        assert ins_request[0]['_id'] in find_request[0]['project']['datasets']


def test_add_bad_fields():
    """Attempt to add datasets with e.g. forbidden fields."""
    session = requests.Session()
    as_user(session, USERS['steward'])
    indata = {'_id': 'asd'}
    indata.update(TEST_DS_LABEL)
    response = make_request(session,
                            '/api/dataset/add',
                            method='POST',
                            data=indata)
    assert response == (None, 400)

    indata = {'timestamp': 'asd'}
    indata.update(TEST_DS_LABEL)
    response = make_request(session,
                            '/api/dataset/add',
                            method='POST',
                            data=indata)
    assert response == (None, 400)

    indata = {'identifiers': ['asd']}
    indata.update(TEST_DS_LABEL)
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
    uuids = [ds['_id'] for ds in response[0]['datasets']]

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
    indata = {'links': [{'description': 'Test description', 'url': 'http://test_url'}],
              'title': 'Test title'}
    indata.update(TEST_DS_LABEL)

    session = requests.Session()
    as_user(session, USERS['steward'])
    indata['projects'] = [ds['_id']
                          for ds in make_request(session,
                                                 '/api/project/random/5')[0]['projects']]
    ins_request = make_request(session,
                               '/api/dataset/add',
                               data=indata, method='POST')

    ds_uuid = ins_request[0]['_id']
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
    while not project['datasets']:
        proj_response = make_request(session, f'/api/project/random')
        assert proj_response[1] == 200
        project = proj_response[0]['projects'][0]
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
    indata = {'links': [{'description': 'Test description', 'url': 'http://test2_url'}],
              'description': 'Test description',
              'title': 'Test2 title'}
    indata.update(TEST_DS_LABEL)

    session = requests.Session()
    as_user(session, USERS['steward'])

    ds_uuid = dataset_for_tests
    responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PUT', data=indata)
    assert [response[1] for response in responses] == [400, 401, 200, 200]
    assert [response[0] for response in responses] == [None]*4
    data = make_request(session, f'/api/dataset/{ds_uuid}')[0]['dataset']
    for field in indata:
        assert data[field] == indata[field]

    new_title = random_string()
    response = make_request(session, f'/api/dataset/{ds_uuid}',
                            method='PUT', data={'title': new_title})
    assert response == (None, 200)
    new_data = make_request(session, f'/api/dataset/{ds_uuid}')[0]['dataset']
    for field in new_data:
        if field == 'title':
            assert new_data[field] == new_title
        else:
            assert new_data[field] == data[field]


def test_update_projects(dataset_for_tests):
    """Confirm that the project associations are updated correcly."""
    session = requests.Session()
    as_user(session, USERS['steward'])

    ds_uuid = dataset_for_tests

    proj_uuid = make_request(session, f'/api/project/random')[0]['projects'][0]['_id']
    indata = {'projects': [proj_uuid]}
    response = make_request(session, f'/api/dataset/{ds_uuid}',
                            method='PUT', data=indata)
    assert response == (None, 200)
    data = make_request(session, f'/api/dataset/{ds_uuid}')[0]['dataset']
    assert proj_uuid in [project['_id'] for project in data['projects']]

    proj_uuid2 = make_request(session, f'/api/project/random')[0]['projects'][0]['_id']
    indata = {'projects': [proj_uuid2]}
    response = make_request(session, f'/api/dataset/{ds_uuid}', method='PUT', data=indata)
    assert response == (None, 200)
    data = make_request(session, f'/api/dataset/{ds_uuid}')[0]['dataset']
    projects = [project['_id'] for project in data['projects']]
    assert proj_uuid2 in projects and not proj_uuid in projects


def test_update_as_owner(dataset_for_tests):
    """Update some datasets as the owner."""
    session = requests.Session()
    as_user(session, USERS['steward'])

    ds_uuid = dataset_for_tests

    project = make_request(session, f'/api/project/random')[0]['projects'][0]
    indata = {'projects': [project['_id']]}
    response = make_request(session, f'/api/dataset/{ds_uuid}',
                            method='PUT', data=indata)
    assert response == (None, 200)

    as_user(session, project['owner'])
    new_title = random_string()
    indata = {'title': new_title}
    response = make_request(session, f'/api/dataset/{ds_uuid}', method='PUT', data=indata)
    assert response == (None, 200)
    data = make_request(session, f'/api/dataset/{ds_uuid}')[0]['dataset']
    assert data['title'] == new_title

    indata = {'creator': 'should not update'}
    response = make_request(session, f'/api/dataset/{ds_uuid}', method='PUT', data=indata)
    assert response == (None, 400)
    data = make_request(session, f'/api/dataset/{ds_uuid}')[0]['dataset']
    assert 'creator' not in data


def test_update_bad(dataset_for_tests):
    """
    Confirm that bad requests will be rejected.

    Should require at least Steward.
    """
    for _ in range(3):
        indata = {'title': 'Updated title'}
        ds_uuid = random_string()
        responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PUT', data=indata)
        assert [response[1] for response in responses] == [400, 401, 404, 404]
        assert [response[0] for response in responses] == [None]*4

        ds_uuid = uuid.uuid4().hex
        responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PUT', data=indata)
        assert [response[1] for response in responses] == [400, 401, 404, 404]
        assert [response[0] for response in responses] == [None]*4

    ds_uuid = dataset_for_tests
    session = requests.Session()
    as_user(session, USERS['steward'])
    indata = {'_id': 'Updated title'}
    response = make_request(session, f'/api/dataset/{ds_uuid}')

    response = make_request(session, f'/api/dataset/{ds_uuid}',
                            method='PUT', data=indata)
    assert response == (None, 400)

    indata = {'_id': 'asd'}
    response = make_request(session, f'/api/dataset/{ds_uuid}',
                            method='PUT', data=indata)
    assert response == (None, 400)

    indata = {'timestamp': 'asd'}
    response = make_request(session, f'/api/dataset/{ds_uuid}',
                            method='PUT', data=indata)
    assert response == (None, 400)
