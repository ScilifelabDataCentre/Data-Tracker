"""Tests for order requests."""
import logging
import uuid

import requests

from helpers import make_request, as_user, make_request_all_roles,\
    USERS, random_string, TEST_LABEL, use_db

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import

logging.getLogger().setLevel(logging.DEBUG)


def test_list_all_orders(use_db):
    """
    Check that all orders in the system are listed.

    Check that the number of fields per order is correct.
    """
    db = use_db
    nr_orders = db['orders'].count_documents({})

    responses = make_request_all_roles(f'/api/order/all', ret_json=True)
    for response in responses:
        if response.role in ('data', 'root'):
            assert response.code == 200
            assert len(response.data['orders']) == nr_orders
            assert set(response.data['orders'][0].keys()) == {'title', '_id',
                                                              'creator', 'receiver'}
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_get_order_permissions(use_db):
    """
    Test permissions for requesting a order.

    Request the orders using users with each unique permission to confirm
    that the correct permissions give/prevent access.
    """
    session = requests.Session()

    db = use_db
    orders = list(db['orders'].aggregate([{'$match': {'creator': {'$type' : "binData"}}},
                                          {'$sample': {'size': 2}}]))
    for order in orders:
        # to simplify comparison
        order['_id'] = str(order['_id'])
        order['receiver'] = str(order['receiver'])
        owner = db['users'].find_one({'_id': order['creator']})
        order['creator'] = str(order['creator'])
        for i, ds in enumerate(order['datasets']):
            order['datasets'][i] = next(db['datasets'].aggregate([{'$match': {'_id': ds}},
                                                                  {'$project': {'_id': 1,
                                                                                'title': 1}}]))
            order['datasets'][i]['_id'] = str(order['datasets'][i]['_id'])

        responses = make_request_all_roles(f'/api/order/{order["_id"]}', ret_json=True)
        for response in responses:
            if response.role in ('data', 'root'):
                assert response.code == 200
                data = response.data['order']
                for field in order:
                    if field == 'datasets':
                        assert len(order[field]) == len(data[field])
                        for ds in order[field]:
                            assert ds in data[field]
                    elif field == '_id':
                        continue
                    else:
                        assert order[field] == data[field]
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        as_user(session, owner['api_key'])
        response = make_request(session, f'/api/order/{order["_id"]}')
        assert response.code == 200
        data = response.data['order']
        for field in order:
            if field == 'datasets':
                assert len(order[field]) == len(data[field])
                for ds in order[field]:
                    assert ds in data[field]
            elif field == '_id':
                continue
            else:
                assert order[field] == data[field]


def test_get_order(use_db):
    """
    Request multiple orders by uuid, one at a time.

    Request the order and confirm that it contains the correct data.
    """
    session = requests.Session()

    db = use_db
    orders = list(db['orders'].aggregate([{'$sample': {'size': 3}}]))
    for order in orders:
        # to simplify comparison
        order['_id'] = str(order['_id'])
        if isinstance(order['receiver'], uuid.UUID):
            order['receiver'] = str(order['receiver'])
        order['creator'] = str(order['creator'])
        for i, ds in enumerate(order['datasets']):
            order['datasets'][i] = next(db['datasets'].aggregate([{'$match': {'_id': ds}},
                                                                  {'$project': {'_id': 1,
                                                                                'title': 1}}]))
            order['datasets'][i]['_id'] = str(order['datasets'][i]['_id'])

        as_user(session, 'data@testers')
        response = make_request(session, f'/api/order/{order["_id"]}')
        assert response.code == 200
        assert response.code == 200
        data = response.data['order']
        for field in order:
            if field == 'datasets':
                assert len(order[field]) == len(data[field])
                for ds in order[field]:
                    assert ds in data[field]
            elif field == '_id':
                continue
            else:
                assert order[field] == data[field]


def test_get_order_bad():
    """
    Request orders using bad identifiers.

    All are expected to return 401, 403, or 404 depending on permissions.
    """
    for _ in range(2):
        responses = make_request_all_roles(f'/api/order/{uuid.uuid4()}')
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data

    for _ in range(2):
        responses = make_request_all_roles(f'/api/order/{random_string()}')
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data


def test_get_log_permissions(use_db):
    """
    Request the logs for multiple orders.

    Confirm that only the correct users can access them.
    """
    session = requests.session()
    db = use_db
    orders = db['orders'].aggregate([{'$sample': {'size': 2}}])
    for order in orders:
        logs = list(db['logs'].find({'data_type': 'order', 'data._id': order['_id']}))
        responses = make_request_all_roles(f'/api/order/{order["_id"]}/log', ret_json=True)
        for response in responses:
            if response.role in ('data', 'root'):
                assert len(response.data['logs']) == len(logs)
                assert response.code == 200
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data
        owner = db['users'].find_one({'_id': order['creator']})
        as_user(session, owner['api_key'])
        response = make_request(session, f'/api/order/{order["_id"]}/log', ret_json=True)
        assert response.code == 200
        assert response.data


def test_get_log(use_db):
    """
    Request the logs for multiple orders.

    Confirm that the logs contain only the intended fields.
    """
    session = requests.session()
    db = use_db
    orders = db['orders'].aggregate([{'$sample': {'size': 2}}])
    for order in orders:
        logs = list(db['logs'].find({'data_type': 'order', 'data._id': order['_id']}))
        as_user(session, USERS['data'])
        response = make_request(session, f'/api/order/{order["_id"]}/log', ret_json=True)
        assert response.data['dataType'] == 'order'
        assert response.data['entryId'] == str(order['_id'])
        assert len(response.data['logs']) == len(logs)
        assert response.code == 200


def test_list_user_orders_permissions(use_db):
    """
    Request orders for multiple users by uuid, one at a time.

    Confirm that only the correct permissions can access the data.
    """
    session = requests.Session()

    db = use_db
    users = db['users'].aggregate([{'$match': {'permissions': {'$in': ['ORDERS_SELF',
                                                                       'DATA_MANAGEMENT']}}},
                                   {'$sample': {'size': 2}}])
    for user in users:
        responses = make_request_all_roles('/api/order/user')
        for response in responses:
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data

        user_orders = list(db['orders'].find({'$or': [{'receiver': user['_id']},
                                                      {'creator': user['_id']}]}))
        responses = make_request_all_roles(f'/api/order/user/{user["_id"]}')
        for response in responses:
            if response.role in ('data', 'root'):
                if user_orders:
                    assert response.code == 200
                    assert response.data
                else:
                    assert response.code == 404
                    assert not response.data
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        if user['auth_id'] != '--facility--':
            as_user(session, user['auth_id'])
        else:
            as_user(session, user['api_key'])
        response = make_request(session, f'/api/order/user')
        if user_orders:
            assert response.code == 200
            assert response.data
        else:
            assert response.code == 404
            assert not response.data


def test_list_user_orders(use_db):
    """
    Request orders for multiple users by uuid, one at a time.

    Request the order list and confirm that it contains the correct data.
    """
    session = requests.Session()

    db = use_db
    users = db['users'].aggregate([{'$match': {'permissions': {'$in': ['ORDERS_SELF',
                                                                       'DATA_MANAGEMENT']}}},
                                   {'$sample': {'size': 2}}])

    for user in users:
        user_orders = list(db['orders'].find({'$or': [{'receiver': user['_id']},
                                                      {'creator': user['_id']}]}))
        order_uuids = [str(order['_id']) for order in user_orders]

        if user['auth_id'] != '--facility--':
            as_user(session, user['auth_id'])
        else:
            as_user(session, user['api_key'])
        response = make_request(session, f'/api/order/user')
        if user_orders:
            assert response.code == 200
            assert response.data
            assert len(user_orders) == len(response.data['orders'])
            for order in response.data['orders']:
                assert order['_id'] in order_uuids
        else:
            assert response.code == 404
            assert not response.data


def test_list_user_orders_bad():
    """
    Request orders for multiple users by uuid, one at a time.

    Confirm that bad requests return nothing
    """
    session = requests.Session()

    as_user(session, USERS['data'])
    for _ in range(2):
        responses = make_request_all_roles(f'/api/order/user/{uuid.uuid4()}')
        for response in responses:
            if response.role in ('data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data

    for _ in range(2):
        responses = make_request_all_roles(f'/api/order/user/{random_string()}')
        for response in responses:
            if response.role in ('data', 'root'):
                assert response.code == 404
            elif response.role == 'no-login':
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data


def test_add_order_get():
    """
    Request data structure from GET add.
    """
    expected = {'creator': '',
                'description': '',
                'extra': {},
                'receiver': '',
                'title': ''}

    responses = make_request_all_roles('/api/order/add', ret_json=True)
    for response in responses:
        if response.role in ('data', 'orders', 'root'):
            assert response.code == 200
            assert response.data == expected
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_add_order_permissions(use_db):
    """
    Add a default dataset using /add POST.

    Test permissions.
    """
    indata = {'title': 'Test title'}
    indata.update(TEST_LABEL)
    responses = make_request_all_roles(f'/api/order/add',
                                       method='POST',
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

    db = use_db
    user_creator = db['users'].find_one({'auth_id': USERS['base']})
    indata = {'creator': user_creator['email']}
    indata.update(TEST_LABEL)
    responses = make_request_all_roles(f'/api/order/add',
                                       method='POST',
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


def test_add_order(use_db):
    """
    Add a default dataset using /add POST.

    Confirm that fields are set correctly.
    """
    db = use_db

    indata = {'description': 'Test description',
              'receiver': 'new_email@example.com',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/order/add',
                                       method='POST',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('orders', 'data', 'root'):
            assert response.code == 200
            assert '_id' in response.data
            assert len(response.data['_id']) == 36
            order = db['orders'].find_one({'_id': uuid.UUID(response.data['_id'])})
            curr_user = db['users'].find_one({'auth_id': USERS[response.role]})
            assert order['description'] == indata['description']
            assert order['receiver'] == indata['receiver']
            assert order['title'] == indata['title']
            assert order['creator'] == curr_user['_id']
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    orders_user = db['users'].find_one({'auth_id': USERS['orders']})
    indata = {'description': 'Test description',
              'creator': str(orders_user['_id']),
              'receiver': 'new_email@example.com',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/order/add',
                                       method='POST',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('data', 'root'):
            assert response.code == 200
            assert '_id' in response.data
            assert len(response.data['_id']) == 36
            order = db['orders'].find_one({'_id': uuid.UUID(response.data['_id'])})
            assert order['description'] == indata['description']
            assert order['receiver'] == indata['receiver']
            assert order['title'] == indata['title']
            assert order['creator'] == orders_user['_id']
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_add_order_log(use_db):
    """
    Add a default dataset using /add POST.

    Confirm that logs are created.
    """
    db = use_db

    indata = {'description': 'Test description',
              'receiver': 'new_email@example.com',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/order/add',
                                       method='POST',
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
    Add a default dataset using /add POST.

    Bad requests.
    """
    indata = {'description': 'Test description',
              'receiver': 'bad_email@asd',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/order/add',
                                       method='POST',
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
              'creator': 'bad_email@asd',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/order/add',
                                       method='POST',
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
              'creator': str(uuid.uuid4()),
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/order/add',
                                       method='POST',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('data', 'root'):
            assert response.code == 400
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_add_dataset_get(use_db):
    """
    Request data structure from GET addDataset.
    """
    expected = {'links': [],
                'description': '',
                'title': '',
                'extra': {}}

    db = use_db
    orders = list(db['orders'].aggregate([{'$sample': {'size': 1}}]))

    for entry in (orders[0]['_id'], random_string(), uuid.uuid4()):
        responses = make_request_all_roles(f'/api/order/{entry}/addDataset', ret_json=True)
        for response in responses:
            if response.role in ('data', 'orders', 'root'):
                assert response.code == 200
                assert response.data == expected
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data


def test_add_dataset_permissions(use_db):
    """
    Add a dataset using .post(addDataset).

    Confirm that permissions are handled correctly.
    """
    session = requests.Session()

    db = use_db
    orders = list(db['orders'].aggregate([{'$sample': {'size': 2}}]))
    indata = {'title': 'Test title'}
    indata.update(TEST_LABEL)
    for order in orders:
        responses = make_request_all_roles(f'/api/order/{order["_id"]}/addDataset',
                                           method='POST',
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
        # as order creator
        owner = db['users'].find_one({'_id': order['creator']})
        as_user(session, owner['api_key'])
        response = make_request(session,
                                f'/api/order/{order["_id"]}/addDataset',
                                method='POST',
                                data=indata)
        assert response.code == 200
        assert '_id' in response.data
        assert len(response.data['_id']) == 36


def test_add_dataset_all_fields(use_db):
    """
    Add a dataset using addDataset.

    Set values in all available fields.
    """
    indata = {'links': [{'description': 'Test description', 'url': 'http://test_url'}],
              'title': 'Test title',
              'description': 'Test description'}
    indata.update(TEST_LABEL)

    db = use_db
    order = next(db['orders'].aggregate([{'$sample': {'size': 1}}]))

    session = requests.session()
    as_user(session, USERS['data'])

    response = make_request(session,
                            f'/api/order/{order["_id"]}/addDataset',
                            method='POST',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    assert '_id' in response.data
    assert len(response.data['_id']) == 36
    indata.update({'_id': response.data['_id']})
    db_ds = db['datasets'].find_one({'_id': uuid.UUID(response.data['_id'])})
    db_o = db['orders'].find_one({'_id': order['_id']})
    db_ds['_id'] = str(db_ds['_id'])
    db_o['datasets'] = [str(uuid) for uuid in db_o['datasets']]
    assert db_ds == indata
    assert response.data['_id'] in db_o['datasets']


def test_add_dataset_log(use_db):
    """
    Confirm that logs are added correctly when datasets are added.

    Check that both there is both update on order and add on dataset.
    """
    indata = {'title': 'Test title'}
    indata.update(TEST_LABEL)

    db = use_db
    order = next(db['orders'].aggregate([{'$sample': {'size': 1}}]))

    session = requests.session()
    as_user(session, USERS['data'])

    order_logs = list(db['logs'].find({'data_type': 'order', 'data._id': order['_id']}))

    response = make_request(session,
                            f'/api/order/{order["_id"]}/addDataset',
                            method='POST',
                            data=indata,
                            ret_json=True)

    order_logs_post = list(db['logs'].find({'data_type': 'order', 'data._id': order['_id']}))
    assert len(order_logs_post) == len(order_logs)+1
    ds_logs_post = list(db['logs'].find({'data_type': 'dataset',
                                         'data._id': uuid.UUID(response.data['_id'])}))
    assert len(ds_logs_post) == 1
    assert ds_logs_post[0]['action']


def test_update_order_permissions(use_db):
    """
    Update an order.

    Test permissions.
    """
    session = requests.Session()

    db = use_db

    orders_user = db['users'].find_one({'auth_id': USERS['orders']})

    orders = list(db['orders'].aggregate([{'$match': {'creator': orders_user['_id']}},
                                          {'$sample': {'size': 3}}]))

    for order in orders:
        for role in USERS:
            as_user(session, USERS[role])
            indata = {'title': f'Test title - updated by {role}'}
            response = make_request(session,
                                    f'/api/order/{order["_id"]}',
                                    method='PUT',
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


def test_update_order(use_db):
    """
    Update existing orders.

    Confirm that fields are set correctly.
    Confirm that logs are created.
    """
    session = requests.Session()

    db = use_db

    orders_user = db['users'].find_one({'auth_id': USERS['orders']})

    orders = list(db['orders'].aggregate([{'$match': {'creator': orders_user['_id']}},
                                          {'$sample': {'size': 2}}]))

    for order in orders:
        for role in USERS:
            as_user(session, USERS[role])
            indata = {'title': f'Test title - updated by {role}',
                      'description': f'Test description - updated by {role}',
                      'receiver': f'new_{role}_email@example.com',
                      'extra': {'updated': 'yes'}}
            indata['extra'].update(TEST_LABEL['extra'])
            current_user = db['users'].find_one({'auth_id': USERS[role]})
            if role in ('data', 'root'):
                indata.update({'creator': str(current_user['_id'])})

            response = make_request(session,
                                    f'/api/order/{order["_id"]}',
                                    method='PUT',
                                    data=indata,
                                    ret_json=True)

            if role in ('orders', 'data', 'root'):
                print(role, indata)
                assert response.code == 200
                assert not response.data
                new_order = db['orders'].find_one({'_id': order['_id']})
                new_order['_id'] = str(new_order['_id'])
                new_order['creator'] = str(new_order['creator'])
                new_order['receiver'] = str(new_order['receiver'])
                new_order['datasets'] = [str(ds_uuid) for ds_uuid in new_order['datasets']]
                for field in indata:
                    assert new_order[field] == indata[field]
                    assert db['logs'].find_one({'data._id': order['_id'],
                                                'action': 'edit',
                                                'data_type': 'order',
                                                'user': current_user['_id']})
            elif role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data


def test_update_order_bad(use_db):
    """
    Add a default dataset using /add POST.

    Bad requests.
    """
    db = use_db

    orders_user = db['users'].find_one({'auth_id': USERS['orders']})
    orders = list(db['orders'].aggregate([{'$match': {'creator': orders_user['_id']}},
                                          {'$sample': {'size': 2}}]))

    for order in orders:
        indata = {'description': 'Test description',
                  'receiver': 'bad_email@asd',
                  'title': 'Test title'}

        responses = make_request_all_roles(f'/api/order/{order["_id"]}',
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
                  'creator': str(uuid.uuid4()),
                  'title': 'Test title'}

        responses = make_request_all_roles(f'/api/order/{order["_id"]}',
                                           method='PUT',
                                           data=indata,
                                           ret_json=True)
        for response in responses:
            if response.role in ('data', 'root'):
                assert response.code == 400
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data


    for _ in range(2):
        indata = {'title': 'Test title'}
        responses = make_request_all_roles(f'/api/order/{uuid.uuid4()}',
                                           method='PUT',
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
        responses = make_request_all_roles(f'/api/order/{random_string}',
                                           method='PUT',
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


def test_add_dataset_bad_fields(use_db):
    """Attempt to add datasets with e.g. forbidden fields."""
    db = use_db
    order = next(db['orders'].aggregate([{'$sample': {'size': 1}}]))
    session = requests.Session()
    as_user(session, USERS['data'])

    indata = {'_id': 'asd'}
    response = make_request(session,
                            f'/api/order/{order["_id"]}/addDataset',
                            method='POST',
                            data=indata)
    assert response.code == 400
    assert not response.data

    indata = {'timestamp': 'asd'}
    response = make_request(session,
                            f'/api/order/{order["_id"]}/addDataset',
                            method='POST',
                            data=indata)
    assert response.code == 400
    assert not response.data

    indata = {'extra': [{'asd': 123}]}
    response = make_request(session,
                            f'/api/order/{order["_id"]}/addDataset',
                            method='POST',
                            data=indata)
    assert response.code == 400
    assert not response.data

    indata = {'links': [{'asd': 123}]}
    response = make_request(session,
                            f'/api/order/{order["_id"]}/addDataset',
                            method='POST',
                            data=indata)
    assert response.code == 400
    assert not response.data

    indata = {'links': 'Some text'}
    response = make_request(session,
                            f'/api/order/{order["_id"]}/addDataset',
                            method='POST',
                            data=indata)
    assert response.code == 400
    assert not response.data


def test_delete_order(use_db):
    """
    Add and delete orders.

    * Check permissions.
    * Delete orders added by the add tests.
    * Confirm that related datasets are deleted.
    * Check that logs are created correctly.
    """
    session = requests.Session()

    db = use_db

    orders_user = db['users'].find_one({'auth_id': USERS['orders']})

    # must be updated if TEST_LABEL is modified
    orders = list(db['orders'].find({'extra.testing': 'yes'}))
    i = 0
    while i < len(orders):
        for role in USERS:
            as_user(session, USERS[role])
            response = make_request(session,
                                    f'/api/order/{orders[i]["_id"]}',
                                    method='DELETE')
            if role in ('orders', 'data', 'root'):
                if role != 'orders' or orders[i]['creator'] == orders_user['_id']:
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
                            f'/api/order/add',
                            data={'title': 'tmp'},
                            method='POST')
    assert response.code == 200
    response = make_request(session,
                            f'/api/order/{response.data["_id"]}',
                            method='DELETE')
    assert response.code == 200
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
