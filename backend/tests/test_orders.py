"""Tests for order requests."""
import json
import time
import uuid
import requests

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import

from helpers import make_request, as_user, make_request_all_roles,\
    USERS, random_string, parse_time


def test_user_orders():
    """
    Retrieve a list of orders belonging to current user.

    Confirm that they actually belong to the user.
    """
    # wait for queries to be ready
    session = requests.Session()
    for _ in range(3):
        response = make_request(session, '/api/project/random')
        expected_orders = response[0]['projects'][0]['orders']
        as_user(session, response[0]['projects'][0]['owner'])
        responses = make_request_all_roles('/api/order/user')
        assert [response[1] for response in responses] == [401, 200, 200, 200]
        for response in responses:
            if response[1] == 401:
                assert not response[0]
            print(response[0])
            orders = [doc['uuid'] for doc in json.loads(response[0])['orders']]
            assert orders == expected_orders


def test_get_order_get_permissions():
    """Test permissions for requesting a order."""
    session = requests.Session()
    orig = make_request(session, '/api/order/random')[0]['orders'][0]
    responses = make_request_all_roles(f'/api/order/{orig["uuid"]}')
    for response in responses:
        assert json.loads(response[0])['order'] == orig
        assert response[1] == 200


def test_get_order():
    """
    Request multiple orders by uuid, one at a time.

    Orders are choosen randomly using /api/order/random.
    """
    session = requests.Session()
    for _ in range(10):
        orig = make_request(session, '/api/order/random')[0]['orders'][0]
        response = make_request(session, f'/api/order/{orig["uuid"]}')
        assert response[1] == 200
        requested = response[0]['order']
        assert orig == requested


def test_get_order_bad():
    """
    Request orders using bad identifiers.

    All are expected to return 404.
    """
    session = requests.Session()
    for _ in range(10):
        response = make_request(session, f'/api/order/{uuid.uuid4().hex}')
        assert response == (None, 404)

    for _ in range(10):
        response = make_request(session, f'/api/order/{random_string()}')
        assert response == (None, 404)
