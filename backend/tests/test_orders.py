"""Tests for order requests."""
import json
import random
import time
import uuid

import requests

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import

from helpers import make_request, as_user, make_request_all_roles,\
    USERS, random_string, parse_time


def test_get_order_get_permissions():
    """Test permissions for requesting a order."""
    session = requests.Session()
    orig = random.choice(make_request(session, '/api/developer/orders')[0]['orders'])
    responses = make_request_all_roles(f'/api/order/{orig["_id"]}')
    for response in responses:
        assert json.loads(response[0])['order'] == orig
        assert response[1] == 200


def test_get_order():
    """
    Request multiple orders by uuid, one at a time.
    """
    session = requests.Session()
    for _ in range(10):
        orig = random.choice(make_request(session, '/api/developer/orders')[0]['orders'])
        response = make_request(session, f'/api/order/{orig["_id"]}')
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
