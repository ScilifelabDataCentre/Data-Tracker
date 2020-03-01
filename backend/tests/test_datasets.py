"""Tests for dataset requests."""
import itertools
import json
import uuid
import requests

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import

from helpers import make_request, as_user, make_request_all_roles,\
    dataset_for_tests, USERS, random_string, parse_time, TEST_LABEL, use_db


def test_list_user_datasets(use_db):
    """
    Choose a few users.

    Compare the ids of datasets from the request to a db query.
    """
    session = requests.Session()
    db = use_db
    users = db['users'].aggregate([{'$sample': {'size': 5}}])
    for user in users:
        user_orders = list(db['orders'].find({'$or': [{'receiver': user['_id']},
                                                      {'creator': user['_id']}],
                                              'datasets': {'$not': {'$size': 0} }},
                                             {'datasets': 1}))
        user_datasets = list(itertools.chain.from_iterable(order['datasets']
                                                           for order in user_orders))
        user_datasets = [str(uuid) for uuid in user_datasets]

        if user['auth_id'] != '--facility--':
            as_user(session, user['auth_id'])
        else:
            as_user(session, user['api_key'])
        response = make_request(session, f'/api/dataset/user')
        assert response.code == 200
        assert len(user_datasets) == len(response.data['datasets'])
        for ds in response.data['datasets']:
            assert ds['_id'] in user_datasets


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


def test_get_dataset_get_permissions(use_db):
    """Test permissions for requesting a dataset."""
    session = requests.Session()
    db = use_db
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


def test_get_dataset_bad():
    """
    Request datasets using bad identifiers.

    All are expected to return 404.
    """
    session = requests.Session()
    for _ in range(5):
        response = make_request(session, f'/api/dataset/{uuid.uuid4().hex}')
        assert response.code == 404
        assert not response.data

    for _ in range(5):
        response = make_request(session, f'/api/dataset/{random_string()}')
        assert response.code == 404
        assert not response.data


def test_delete_dataset(use_db):
    """
    Add and delete datasets.

    * Check permissions.
    * Delete orders added by the add tests.
    * Confirm that related dataset entries in orders and projects are deleted.
    * Check that logs are created correctly.
    """
    session = requests.Session()

    db = use_db

    orders_user = db['users'].find_one({'auth_id': USERS['data']})

    # must be updated if TEST_LABEL is modified
    datasets = list(db['datasets'].find({'extra.testing': 'yes'}))
    i = 0
    while i < len(datasets):
        for role in USERS:
            as_user(session, USERS[role])
            order = db['orders'].find_one({'datasets': datasets[i]['_id']})
            projects = list(db['projects'].find({'datasets': datasets[i]['_id']}))
            response = make_request(session,
                                    f'/api/dataset/{datasets[i]["_id"]}',
                                    method='DELETE')
            current_user = db['users'].find_one({'auth_id': USERS[role]})
            if role == 'no-login':
                assert response.code == 401
                assert not response.data
            elif role in ('data', 'root') or order['creator'] == current_user['_id']:
                assert response.code == 200
                assert not response.data
                assert not db['datasets'].find_one({'_id': datasets[i]['_id']})
                assert db['logs'].find_one({'data._id': datasets[i]['_id'],
                                            'action': 'delete',
                                            'data_type': 'dataset'})
                assert not list(db['orders'].find({'datasets': datasets[i]['_id']}))
                assert not list(db['projects'].find({'datasets': datasets[i]['_id']}))
                assert db['logs'].find_one({'data._id': order['_id'],
                                            'action': 'edit',
                                            'data_type': 'order',
                                            'comment': f'Deleted dataset {datasets[i]["_id"]}'})
                p_logs = list(db['logs'].find({'action': 'edit',
                                               'data_type': 'project',
                                               'comment': f'Deleted dataset {datasets[i]["_id"]}'}))
                assert len(p_logs) == len(projects)
                i += 1
                if i >= len(datasets):
                    break
            else:
                assert response.code == 403
                assert not response.data


def test_delete_order_bad():
    """Attempt bad order delete requests."""
    session = requests.Session()

    as_user(session, USERS['data'])
    for _ in range(2):
        response = make_request(session,
                                f'/api/order/{random_string()}',
                                method='DELETE')
    assert response.code == 404
    assert not response.data

    for _ in range(2):
        response = make_request(session,
                                f'/api/order/{uuid.uuid4()}',
                                method='DELETE')
    assert response.code == 404
    assert not response.data


def test_delete(use_db):
    """
    Delete all datasets that were created by the add tests, one at a time.
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
    indata.update(TEST_LABEL)

    session = requests.Session()
    as_user(session, USERS['data'])
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
    as_user(session, USERS['data'])
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
    for response in responses:
        if response.role in ('orders', 'data', 'root'):
            assert response.code == 200
        elif response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

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
    indata.update(TEST_LABEL)

    session = requests.Session()
    as_user(session, USERS['data'])

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
    as_user(session, USERS['data'])

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
    as_user(session, USERS['data'])
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


def test_list_datasets():
    """
    Request a list of all datasets.

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles('/api/dataset/all', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['datasets']) == 500


