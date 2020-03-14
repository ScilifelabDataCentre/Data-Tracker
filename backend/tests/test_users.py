"""Tests for dataset requests."""
import json
import requests

from helpers import make_request, as_user, make_request_all_roles, USERS
# pylint: disable=redefined-outer-name

def test_logout():
    """Assure that session is cleared after logging out."""
    session = requests.Session()
    as_user(session, USERS['root'])
    response = make_request(session, '/api/user/me')
    for field in response.data['user']:
        assert response.data['user'][field]
    response = make_request(session, '/api/user/logout', ret_json=False)
    response = make_request(session, '/api/user/me')
    for field in response.data['user']:
        assert not response.data['user'][field]


def test_list_users():
    """
    Retrieve list of users.

    Assert that admin is required.
    """
    responses = make_request_all_roles('/api/user/',
                                       ret_json=True)
    for response in responses:
        if response.role in ('users', 'root'):
            assert response.code == 200
            assert len(response.data['users']) == 137
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_list_info():
    """
    Retrieve info about current user.
    """
    responses = make_request_all_roles('/api/user/me',
                                       ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['user']) == 5
        if response.role != 'no-login':
            assert response.data['user']['name'] == f'{response.role.capitalize()} Test'


def test_country_list():
    """
    Request a list of countries

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles('/api/user/countries',
                                       ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['countries']) == 240
