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
            # only data managers or owners may delete datasets
            elif role in ('data', 'root') or order['creator'] == current_user['_id']:
                assert response.code == 200
                assert not response.data
                # confirm that dataset does not exist in db and that a log has been created
                assert not db['datasets'].find_one({'_id': datasets[i]['_id']})
                assert db['logs'].find_one({'data._id': datasets[i]['_id'],
                                            'action': 'delete',
                                            'data_type': 'dataset'})
                # confirm that no references to the dataset exist in orders or project
                assert not list(db['orders'].find({'datasets': datasets[i]['_id']}))
                assert not list(db['projects'].find({'datasets': datasets[i]['_id']}))
                # confirm that the removal of the references are logged.
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
        assert response.code == 404
        assert not response.data
        ds_uuid = uuid.uuid4().hex
        response = make_request(session,
                                f'/api/dataset/{ds_uuid}',
                                method='DELETE')
        assert response.code == 404
        assert not response.data


def test_update_permissions(use_db, dataset_for_tests):
    """
    Test the permissions for the request.

    Should require at least Steward or being the owner of the dataset.
    """
    db = use_db
    ds_uuid = dataset_for_tests
    print(db['datasets'].find_one({'_id': ds_uuid}))
    print(db['orders'].find_one({'datasets': ds_uuid}))
    indata = {'title': 'Updated title'}
    responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PATCH', data=indata)
    for response in responses:
        if response.role in ('base', 'orders', 'data', 'root'):
            assert response.code == 200
        elif response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data


def test_update_empty(dataset_for_tests):
    """
    Confirm response 400 to an empty update request

    Should require at least Steward or being the owner of the dataset.
    """
    ds_uuid = dataset_for_tests
    indata = {}
    responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PATCH', data=indata)
    for response in responses:
        if response.role in ('base', 'orders', 'data', 'root'):
            assert response.code == 200
        elif response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data


def test_update(use_db, dataset_for_tests):
    """
    Update a dataset multiple times. Confirm that the update is done correctly.

    Should require at least Steward.
    """
    ds_uuid = dataset_for_tests
    db = use_db
    indata = {'links': [{'description': 'Test description from update', 'url': 'http://test_url'}],
              'description': 'Test description - updated',
              'title': 'Test title - updated'}
    indata.update(TEST_LABEL)

    session = requests.Session()
    as_user(session, USERS['data'])

    response = make_request(session, f'/api/dataset/{ds_uuid}', method='PATCH', data=indata)
    assert response.code == 200
    assert not response.data

    dataset = db['datasets'].find_one({'_id': ds_uuid})
    for field in indata:
        assert dataset[field] == indata[field]
    assert db['logs'].find_one({'data._id': ds_uuid,
                                'action': 'edit',
                                'data_type': 'dataset'})


def test_update_bad(dataset_for_tests):
    """
    Confirm that bad requests will be rejected.

    Should require at least Steward.
    """
    for _ in range(2):
        indata = {'title': 'Updated title'}
        ds_uuid = random_string()
        responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PATCH', data=indata)
        for response in responses:
            if response.role in ('base', 'orders', 'data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
            else:
                assert response.code == 404
                assert not response.data

        ds_uuid = uuid.uuid4().hex
        responses = make_request_all_roles(f'/api/dataset/{ds_uuid}', method='PATCH', data=indata)
        for response in responses:
            if response.role in ('base', 'orders', 'data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
            else:
                assert response.code == 404
                assert not response.data

    ds_uuid = dataset_for_tests
    session = requests.Session()
    as_user(session, USERS['data'])
    indata = {'title': ''}
    response = make_request(session, f'/api/dataset/{ds_uuid}',
                            method='PATCH', data=indata)
    assert response.code == 400
    assert not response.data

    indata = {'extra': 'asd'}
    response = make_request(session, f'/api/dataset/{ds_uuid}',
                            method='PATCH', data=indata)
    assert response.code == 400
    assert not response.data

    indata = {'timestamp': 'asd'}
    response = make_request(session, f'/api/dataset/{ds_uuid}',
                            method='PATCH', data=indata)
    assert response.code == 400
    assert not response.data


def test_list_datasets():
    """
    Request a list of all datasets.

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles('/api/dataset/', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['datasets']) == 500
