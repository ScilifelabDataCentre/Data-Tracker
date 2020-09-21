"""Tests for order requests."""
import logging
import uuid

import requests

import structure
import utils

from helpers import make_request, as_user, make_request_all_roles,\
    USERS, random_string, TEST_LABEL, mdb, USER_RE

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import

logging.getLogger().setLevel(logging.DEBUG)


def test_get_order_permissions(mdb):
    """
    Test permissions for requesting a order.

    Request the orders using users with each unique permission to confirm
    that the correct permissions give/prevent access.
    """
    session = requests.Session()

    db = mdb
    orders = list(db['orders'].aggregate([{'$match': {'auth_ids': USER_RE}},
                                          {'$sample': {'size': 2}}]))
    for order in orders:
        owner = db['users'].find_one({'_id': order['editors'][0]})
        responses = make_request_all_roles(f'/api/order/{order["_id"]}/', ret_json=True)
        for response in responses:
            if response.role in ('data', 'root'):
                assert response.code == 200
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        as_user(session, owner['auth_id'])
        response = make_request(session, f'/api/order/{order["_id"]}/')
        assert response.code == 200
        data = response.data['order']


def test_get_order(mdb):
    """
    Request multiple orders by uuid, one at a time.

    Request the order and confirm that it contains the correct data.
    """
    session = requests.Session()
    as_user(session, USERS['data'])

    db = mdb
    orders = list(db['orders'].aggregate([{'$sample': {'size': 3}}]))
    for order in orders:
        # to simplify comparison
        order['_id'] = str(order['_id'])
        # user entries
        for key in ('authors', 'generators', 'editors'):
            order[key] = [utils.user_uuid_data(str(entry), db) for entry in order[key]]
        order['organisation'] = utils.user_uuid_data(order['organisation'], db)

        for i, ds in enumerate(order['datasets']):
            order['datasets'][i] = next(db['datasets'].aggregate([{'$match': {'_id': ds}},
                                                                  {'$project': {'_id': 1,
                                                                                'title': 1}}]))
            order['datasets'][i]['_id'] = str(order['datasets'][i]['_id'])


        response = make_request(session, f'/api/order/{order["_id"]}/')
        assert response.code == 200
        assert response.code == 200
        data = response.data['order']
        assert len(order) == len(data)
        for field in order:
            if field == 'datasets':
                assert len(order[field]) == len(data[field])
                for ds in order[field]:
                    assert ds in data[field]
            elif field == 'tags_standard':
                assert order[field] == data['tagsStandard']
            elif field == 'tags_user':
                assert order[field] == data['tagsUser']
            else:
                assert order[field] == data[field]



def test_get_order_structure():
    """Request the order structure and confirm that it matches the official one"""
    session = requests.Session()
    as_user(session, USERS['data'])

    reference = structure.order()
    reference['_id'] = ''
    reference['tagsStandard'] = reference['tags_standard']
    del reference['tags_standard']
    reference['tagsUser'] = reference['tags_user']
    del reference['tags_user']

    response = make_request(session, '/api/order/base/')
    assert response.code == 200
    data = response.data['order']
    assert data == reference


def test_get_order_bad():
    """
    Request orders using bad identifiers.

    All are expected to return 401, 403, or 404 depending on permissions.
    """
    for _ in range(2):
        responses = make_request_all_roles(f'/api/order/{uuid.uuid4()}/')
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data

    for _ in range(2):
        responses = make_request_all_roles(f'/api/order/{random_string()}/')
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data


def test_get_order_logs_permissions(mdb):
    """
    Get order logs.

    Assert that DATA_MANAGEMENT or user in creator is required.
    """
    db = mdb
    order_data = db['orders'].aggregate([{'$sample': {'size': 1}}]).next()
    user_data = db['users'].find_one({'_id': {'$in': order_data['editors']}})
    responses = make_request_all_roles(f'/api/order/{order_data["_id"]}/log/',
                                       ret_json=True)
    for response in responses:
        if response.role in ('data', 'root'):
            assert response.code == 200
            assert 'logs' in response.data
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    session = requests.Session()

    as_user(session, user_data['auth_ids'][0])
    response = make_request(session,
                            f'/api/order/{order_data["_id"]}/log/',
                            ret_json=True)

    assert response.code == 200
    assert 'logs' in response.data


def test_get_order_logs(mdb):
    """
    Request the logs for multiple orders.

    Confirm that the logs contain only the intended fields.
    """
    session = requests.session()
    db = mdb
    orders = db['orders'].aggregate([{'$sample': {'size': 2}}])
    for order in orders:
        logs = list(db['logs'].find({'data_type': 'order', 'data._id': order['_id']}))
        as_user(session, USERS['data'])
        response = make_request(session, f'/api/order/{order["_id"]}/log/', ret_json=True)
        assert response.data['dataType'] == 'order'
        assert response.data['entryId'] == str(order['_id'])
        assert len(response.data['logs']) == len(logs)
        assert response.code == 200


def test_get_order_logs_bad():
    """
    Request the logs for multiple orders.

    Confirm that bad identifiers give response 404.
    """
    session = requests.session()
    for _ in range(2):
        as_user(session, USERS['data'])
        response = make_request(session, f'/api/order/{uuid.uuid4()}/log/', ret_json=True)
        assert response.code == 200
        response = make_request(session, f'/api/order/{random_string()}/log/', ret_json=True)
        assert response.code == 404


def test_list_user_orders_permissions(mdb):
    """
    Request orders for multiple users by uuid, one at a time.

    Confirm that only the correct permissions can access the data.
    """
    session = requests.Session()

    db = mdb
    users = db['users'].aggregate([{'$match': {'permissions': {'$in': ['ORDERS_SELF',
                                                                       'DATA_MANAGEMENT']}}},
                                   {'$sample': {'size': 2}}])
    for user in users:
        responses = make_request_all_roles('/api/order/user/', ret_json=True)
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 200
                assert len(response.data['orders']) == 0
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        user_orders = list(db['orders'].find({'editors': user['_id']}))
        responses = make_request_all_roles(f'/api/order/user/{user["_id"]}/', ret_json=True)
        for response in responses:
            if response.role in ('data', 'root'):
                if user_orders:
                    assert response.code == 200
                    assert response.data
                else:
                    assert response.code == 200
                    assert len(response.data['orders']) == 0
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        as_user(session, user['auth_ids'][0])
        response = make_request(session, '/api/order/user/')
        if user_orders:
            assert response.code == 200
            assert response.data
        else:
            assert response.code == 200
            assert len(response.data['orders']) == 0


def test_list_user_orders(mdb):
    """
    Request orders for multiple users by uuid, one at a time.

    Request the order list and confirm that it contains the correct data.
    """
    session = requests.Session()

    db = mdb
    users = db['users'].aggregate([{'$match': {'permissions': {'$in': ['ORDERS_SELF',
                                                                       'DATA_MANAGEMENT']}}},
                                   {'$sample': {'size': 2}}])

    for user in users:
        user_orders = list(db['orders'].find({'editors': user['_id']}))
        order_uuids = [str(order['_id']) for order in user_orders]

        as_user(session, user['auth_ids'][0])
        response = make_request(session, '/api/order/user/')
        if user_orders:
            assert response.code == 200
            assert response.data
            assert len(user_orders) == len(response.data['orders'])
            for order in response.data['orders']:
                assert order['_id'] in order_uuids
        else:
            assert response.code == 200
            assert len(response.data['orders']) == 0


def test_list_user_orders_bad():
    """
    Request orders for multiple users by uuid, one at a time.

    Confirm that bad requests return nothing
    """
    session = requests.Session()

    as_user(session, USERS['data'])
    for _ in range(2):
        responses = make_request_all_roles(f'/api/order/user/{uuid.uuid4()}/')
        for response in responses:
            if response.role in ('data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

    for _ in range(2):
        responses = make_request_all_roles(f'/api/order/user/{random_string()}/')
        for response in responses:
            if response.role in ('data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data


def test_add_order_permissions():
    """
    Add an order.

    Test permissions.
    """
    indata = {'title': 'Test title'}
    indata.update(TEST_LABEL)
    responses = make_request_all_roles('/api/order/',
                                       method='PUT',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('orders', 'data', 'root'):
            assert response.code == 200
            assert '_id' in response.data
            assert len(response.data['_id']) == 36
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_add_order(mdb):
    """
    Add an order.

    Confirm that fields are set correctly.
    """
    db = mdb

    indata = {'description': 'Test description',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles('/api/order/',
                                       method='PUT',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('orders', 'data', 'root'):
            assert response.code == 200
            assert '_id' in response.data
            assert len(response.data['_id']) == 36
            order = db['orders'].find_one({'_id': uuid.UUID(response.data['_id'])})
            curr_user = db['users'].find_one({'auth_ids': USERS[response.role]})
            assert order['description'] == indata['description']
            assert order['title'] == indata['title']
            assert curr_user['_id'] in order['editors']
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    orders_user = db['users'].find_one({'auth_ids': USERS['orders']})
    indata = {'description': 'Test description',
              'authors': [str(orders_user['_id'])],
              'editors': [str(orders_user['_id'])],
              'generators': [str(orders_user['_id'])],
              'organisation': str(orders_user['_id']),
              'tags_standard': {'collection': 'testing'},
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles('/api/order/',
                                       method='PUT',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('orders', 'data', 'root'):
            assert response.code == 200
            assert '_id' in response.data
            assert len(response.data['_id']) == 36
            order = db['orders'].find_one({'_id': uuid.UUID(response.data['_id'])})

            user_list = [orders_user['_id']]
            for field in ('description', 'title', 'tags_standard', 'tags_user'):
                assert order[field] == indata[field]
            for field in ('authors', 'generators'):
                assert order[field] == user_list
            curr_user = db['users'].find_one({'auth_ids': USERS[response.role]})

            assert set(order['editors']) == set([uuid.UUID(entry) for entry in indata[field]] +
                                                [curr_user['_id']])
            assert order['organisation'] == uuid.UUID(indata['organisation'])
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_add_order_log(mdb):
    """
    Add an order.

    Confirm that logs are created.
    """
    db = mdb

    indata = {'description': 'Test description',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles('/api/order/',
                                       method='PUT',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('orders', 'data', 'root'):
            assert response.code == 200
            assert '_id' in response.data
            assert len(response.data['_id']) == 36
            order = db['orders'].find_one({'_id': uuid.UUID(response.data['_id'])})
            logs = list(db['logs'].find({'data_type': 'order',
                                         'data._id': uuid.UUID(response.data['_id'])}))
            assert len(logs) == 1
            assert logs[0]['data'] == order
            assert logs[0]['action'] == 'add'
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_add_order_bad():
    """
    Add an order.

    Bad requests.
    """
    indata = {'description': 'Test description',
              'organisation': 'url@bad.se',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles('/api/order/',
                                       method='PUT',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('orders', 'data', 'root'):
            assert response.code == 400
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    indata = {'description': 'Test description',
              'authors': [str(uuid.uuid4())],
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles('/api/order/',
                                       method='PUT',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('orders', 'data', 'root'):
            assert response.code == 400
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    session = requests.Session()
    as_user(session, USERS['data'])
    indata = {'_id': str(uuid.uuid4()),
              'title': 'Test title'}
    indata.update(TEST_LABEL)
    response = make_request(session,
                            '/api/order/',
                            method='PUT',
                            data=indata,
                            ret_json=True)
    assert response.code == 403
    assert not response.data


def test_add_dataset_permissions(mdb):
    """
    Add a dataset using .post(addDataset).

    Confirm that permissions are handled correctly.
    """
    session = requests.Session()

    db = mdb
    orders = db['orders'].aggregate([{'$sample': {'size': 2}}])
    indata = {'title': 'Test title'}
    indata.update(TEST_LABEL)
    for order in orders:
        responses = make_request_all_roles(f'/api/order/{order["_id"]}/dataset/',
                                           method='PUT',
                                           data=indata,
                                           ret_json=True)
        for response in responses:
            if response.role in ('data', 'root'):
                assert response.code == 200
                assert '_id' in response.data
                assert len(response.data['_id']) == 36
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        # as order editor
        owner = db['users'].find_one({'_id': order['editors'][0]})
        as_user(session, owner['auth_ids'][0])
        response = make_request(session,
                                f'/api/order/{order["_id"]}/dataset/',
                                method='PUT',
                                data=indata)
        assert response.code == 200
        assert '_id' in response.data
        assert len(response.data['_id']) == 36


def test_add_dataset(mdb):
    """
    Add a dataset using POST dataset.

    Set values in all available fields.
    """
    indata = {'title': 'Test title',
              'description': 'Test description'}
    indata.update(TEST_LABEL)

    db = mdb
    order = next(db['orders'].aggregate([{'$sample': {'size': 1}}]))

    session = requests.session()
    as_user(session, USERS['data'])

    response = make_request(session,
                            f'/api/order/{order["_id"]}/dataset/',
                            method='PUT',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    assert '_id' in response.data
    assert len(response.data['_id']) == 36
    indata.update({'_id': response.data['_id']})
    db_ds = db['datasets'].find_one({'_id': uuid.UUID(response.data['_id'])})
    db_o = db['orders'].find_one({'_id': order['_id']})
    db_ds['_id'] = str(db_ds['_id'])
    db_o['datasets'] = [str(ds_uuid) for ds_uuid in db_o['datasets']]
    for field in indata:
        assert db_ds[field] == indata[field]
    assert response.data['_id'] in db_o['datasets']


def test_add_dataset_log(mdb):
    """
    Confirm that logs are added correctly when datasets are added.

    Check that both there is both update on order and add on dataset.
    """
    indata = {'title': 'Test title'}
    indata.update(TEST_LABEL)

    db = mdb
    order = next(db['orders'].aggregate([{'$sample': {'size': 1}}]))

    session = requests.session()
    as_user(session, USERS['data'])

    order_logs = list(db['logs'].find({'data_type': 'order', 'data._id': order['_id']}))

    response = make_request(session,
                            f'/api/order/{order["_id"]}/dataset/',
                            method='PUT',
                            data=indata,
                            ret_json=True)

    order_logs_post = list(db['logs'].find({'data_type': 'order', 'data._id': order['_id']}))
    assert len(order_logs_post) == len(order_logs)+1
    ds_logs_post = list(db['logs'].find({'data_type': 'dataset',
                                         'data._id': uuid.UUID(response.data['_id'])}))
    assert len(ds_logs_post) == 1
    assert ds_logs_post[0]['action']


def test_add_dataset_bad_fields(mdb):
    """Attempt to add datasets with e.g. forbidden fields."""
    db = mdb
    order = next(db['orders'].aggregate([{'$sample': {'size': 1}}]))
    session = requests.Session()
    as_user(session, USERS['data'])

    indata = {'_id': 'asd',
              'title': 'test title'}
    response = make_request(session,
                            f'/api/order/{order["_id"]}/dataset/',
                            method='PUT',
                            data=indata)
    assert response.code == 403
    assert not response.data

    indata = {'timestamp': 'asd',
              'title': 'test title'}
    response = make_request(session,
                            f'/api/order/{order["_id"]}/dataset/',
                            method='PUT',
                            data=indata)
    assert response.code == 400
    assert not response.data

    indata = {'extra': [{'asd': 123}],
              'title': 'test title'}
    response = make_request(session,
                            f'/api/order/{order["_id"]}/dataset/',
                            method='PUT',
                            data=indata)
    assert response.code == 400
    assert not response.data

    indata = {'links': [{'asd': 123}],
              'title': 'test title'}
    response = make_request(session,
                            f'/api/order/{order["_id"]}/dataset/',
                            method='PUT',
                            data=indata)
    assert response.code == 400
    assert not response.data

    indata = {'links': 'Some text',
              'title': 'test title'}
    response = make_request(session,
                            f'/api/order/{order["_id"]}/dataset/',
                            method='PUT',
                            data=indata)
    assert response.code == 400
    assert not response.data


def test_update_order_permissions(mdb):
    """
    Update an order.

    Test permissions.
    """
    session = requests.Session()

    db = mdb

    orders_user = db['users'].find_one({'auth_ids': USERS['orders']})

    orders = list(db['orders'].aggregate([{'$match': {'editors': orders_user['_id']}},
                                          {'$sample': {'size': 3}}]))

    for order in orders:
        for role in USERS:
            as_user(session, USERS[role])
            indata = {'title': f'Test title - updated by {role}'}
            response = make_request(session,
                                    f'/api/order/{order["_id"]}/',
                                    method='PATCH',
                                    data=indata,
                                    ret_json=True)
            if role in ('orders', 'data', 'root'):
                assert response.code == 200
                assert not response.data
                new_order = db['orders'].find_one({'_id': order['_id']})
                assert new_order['title'] == f'Test title - updated by {role}'
            elif role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data


def test_update_order_data(mdb):
    """
    Update existing orders.

    Confirm that fields are set correctly.
    Confirm that logs are created.
    """
    session = requests.Session()

    db = mdb

    orders_user = db['users'].find_one({'auth_ids': USERS['orders']})

    orders = list(db['orders'].aggregate([{'$match': {'editors': orders_user['_id']}},
                                          {'$sample': {'size': 2}}]))

    assert len(orders) > 0

    as_user(session, USERS['orders'])
    for order in orders:
        indata = {'title': 'Test title - updated by orders user',
                  'description': 'Test description - updated by orders user',
                  'tags_user': {'updated': 'yes'}}
        indata['tags_user'].update(TEST_LABEL['tags_user'])

        response = make_request(session,
                                f'/api/order/{order["_id"]}/',
                                method='PATCH',
                                data=indata,
                                ret_json=True)

        assert response.code == 200
        assert not response.data
        new_order = db['orders'].find_one({'_id': order['_id']})
        new_order['_id'] = str(new_order['_id'])
        new_order['authors'] = [str(entry) for entry in new_order['authors']]
        new_order['generators'] = [str(entry) for entry in new_order['generators']]
        new_order['organisation'] = str(new_order['organisation'])
        new_order['datasets'] = [str(ds_uuid) for ds_uuid in new_order['datasets']]
        for field in indata:
            assert new_order[field] == indata[field]
            assert db['logs'].find_one({'data._id': order['_id'],
                                        'action': 'edit',
                                        'data_type': 'order',
                                        'user': orders_user['_id']})


def test_update_order_bad(mdb):
    """
    Update an existing order.

    Bad requests.
    """
    db = mdb

    orders_user = db['users'].find_one({'auth_ids': USERS['orders']})
    orders = list(db['orders'].aggregate([{'$match': {'editors': orders_user['_id']}},
                                          {'$sample': {'size': 2}}]))

    assert len(orders) > 0

    for order in orders:
        indata = {'description': 'Test description',
                  'authors': str(uuid.uuid4()),
                  'title': 'Test title'}
        responses = make_request_all_roles(f'/api/order/{order["_id"]}/',
                                           method='PATCH',
                                           data=indata,
                                           ret_json=True)
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 400
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        indata = {'description': 'Test description',
                  'editors': str(orders_user['_id']),
                  'title': 'Test title'}
        responses = make_request_all_roles(f'/api/order/{order["_id"]}/',
                                           method='PATCH',
                                           data=indata,
                                           ret_json=True)
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 400
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        indata = {'description': 'Test description',
                  'editors': [str(uuid.uuid4())],
                  'title': 'Test title'}
        responses = make_request_all_roles(f'/api/order/{order["_id"]}/',
                                           method='PATCH',
                                           data=indata,
                                           ret_json=True)
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 400
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data


    for _ in range(2):
        indata = {'title': 'Test title'}
        responses = make_request_all_roles(f'/api/order/{uuid.uuid4()}/',
                                           method='PATCH',
                                           data=indata,
                                           ret_json=True)
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        indata = {'title': 'Test title'}
        responses = make_request_all_roles(f'/api/order/{random_string}/',
                                           method='PATCH',
                                           data=indata,
                                           ret_json=True)
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data


def test_delete_order(mdb):
    """
    Add and delete orders.

    * Check permissions.
    * Delete orders added by the add tests.
    * Confirm that related datasets are deleted.
    * Check that logs are created correctly.
    """
    session = requests.Session()

    db = mdb

    orders_user = db['users'].find_one({'auth_ids': USERS['orders']})

    # must be updated if TEST_LABEL is modified
    orders = list(db['orders'].find({'tags_user.testing': 'true'}))
    i = 0
    while i < len(orders):
        for role in USERS:
            as_user(session, USERS[role])
            response = make_request(session,
                                    f'/api/order/{orders[i]["_id"]}/',
                                    method='DELETE')
            if role in ('orders', 'data', 'root'):
                if role != 'orders' or orders_user['_id'] in orders[i]['editors']:
                    assert response.code == 200
                    assert not response.data
                    assert not db['orders'].find_one({'_id': orders[i]['_id']})
                    assert db['logs'].find_one({'data._id': orders[i]['_id'],
                                                'action': 'delete',
                                                'data_type': 'order'})
                    for dataset_uuid in orders[i]['datasets']:
                        assert not db['datasets'].find_one({'_id': dataset_uuid})
                        assert db['logs'].find_one({'data._id': dataset_uuid,
                                                    'action': 'delete',
                                                    'data_type': 'dataset'})
                    i += 1
                    if i >= len(orders):
                        break
                else:
                    assert response.code == 403
                    assert not response.data
            elif role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

    as_user(session, USERS['orders'])
    response = make_request(session,
                            '/api/order/',
                            data={'title': 'tmp'},
                            method='PUT')
    assert response.code == 200
    response = make_request(session,
                            f'/api/order/{response.data["_id"]}/',
                            method='DELETE')
    assert response.code == 200
    assert not response.data


def test_delete_order_bad():
    """Attempt bad order delete requests."""
    session = requests.Session()

    as_user(session, USERS['data'])
    for _ in range(2):
        response = make_request(session,
                                f'/api/order/{random_string()}/',
                                method='DELETE')
    assert response.code == 404
    assert not response.data

    for _ in range(2):
        response = make_request(session,
                                f'/api/order/{uuid.uuid4()}/',
                                method='DELETE')
    assert response.code == 404
    assert not response.data


def test_list_all_orders(mdb):
    """
    Check that all orders in the system are listed.

    Check that the number of fields per order is correct.
    """
    db = mdb
    nr_orders = db['orders'].count_documents({})

    responses = make_request_all_roles('/api/order/', ret_json=True)
    for response in responses:
        if response.role in ('data', 'root'):
            assert response.code == 200
            assert len(response.data['orders']) == nr_orders
            assert set(response.data['orders'][0].keys()) == {'title',
                                                              '_id'}
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data

        elif response.role == 'orders':
            assert response.code == 200
            assert len(response.data['orders']) == 0

        else:
            assert response.code == 403
            assert not response.data
