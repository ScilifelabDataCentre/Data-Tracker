"""Tests for order requests."""
import json
import random
import uuid

import requests

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import

from helpers import make_request, as_user, make_request_all_roles,\
    USERS, random_string, parse_time, db_connection


def test_get_order_get_permissions():
    """
    Test permissions for requesting a order.

    Request the orders using users with each unique permission to confirm
    that the correct permissions give/prevent access.
    """
    session = requests.Session()

    db = db_connection()
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
                                                                  {'$project': {'_id': 0,
                                                                                'uuid': '$_id',
                                                                                'title': 1}}]))
            order['datasets'][i]['uuid'] = str(order['datasets'][i]['uuid'])

        responses = make_request_all_roles(f'/api/order/{order["_id"]}')
        for response in responses:
            if response.role in ('data', 'root'):
                assert response.code == 200
                assert json.loads(response.data)['order'] == order
            elif response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data

        as_user(session, owner['api_key'])
        response = make_request(session, f'/api/order/{order["_id"]}')
        assert response.code == 200
        assert response.data['order'] == order
    

def test_get_order():
    """
    Request multiple orders by uuid, one at a time.

    Request the order and confirm that it contains the correct data.
    """
    session = requests.Session()

    db = db_connection()
    orders = list(db['orders'].aggregate([{'$sample': {'size': 10}}]))
    for order in orders:
        # to simplify comparison
        order['_id'] = str(order['_id'])
        if isinstance(order['receiver'], uuid.UUID):
            order['receiver'] = str(order['receiver'])
        order['creator'] = str(order['creator'])
        for i, ds in enumerate(order['datasets']):
            order['datasets'][i] = next(db['datasets'].aggregate([{'$match': {'_id': ds}},
                                                                  {'$project': {'_id': 0,
                                                                                'uuid': '$_id',
                                                                                'title': 1}}]))
            order['datasets'][i]['uuid'] = str(order['datasets'][i]['uuid'])

        as_user(session, 'data@testers')
        response = make_request(session, f'/api/order/{order["_id"]}')
        print(response)
        assert response.code == 200
        assert response.data['order'] == order


def test_get_order_bad():
    """
    Request orders using bad identifiers.

    All are expected to return 401, 403, or 404 depending on permissions.
    """
    session = requests.Session()
    for _ in range(5):
        responses = make_request_all_roles(f'/api/order/{uuid.uuid4()}')
        for response in responses:
            print(response.role)
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 404
            elif response.role in ('no-login'):
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data

    for _ in range(5):
        responses = make_request_all_roles(f'/api/order/{random_string()}')
        for response in responses:
            print(response.role)
            if response.role in ('orders', 'data', 'root'):
                assert response.code == 404
            elif response.role in ('no-login'):
                assert response.code == 401
            else:
                assert response.code == 403
            assert not response.data
