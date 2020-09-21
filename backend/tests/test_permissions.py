"""Tests for permission levels."""

import json

import requests

import helpers

# pylint: disable=redefined-outer-name


def test_request_no_permissions_required():
    """Request target with no permission requirements."""
    responses = helpers.make_request_all_roles('/api/developer/hello', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert response.data == {'test': "success"}


def test_request_login_required():
    """Request target with no permission requirements apart from being logged in."""
    responses = helpers.make_request_all_roles('/api/developer/loginhello', ret_json=True)
    for response in responses:
        if response.role != 'no-login':
            assert response.code == 200
            assert response.data == {'test': "success"}
        else:
            assert response.code == 401
            assert not response.data


def test_request_permission_orders_self():
    """Request requiring ORDERS permissions."""
    responses = helpers.make_request_all_roles('/api/developer/hello/ORDERS', ret_json=True)
    for response in responses:
        if response.role in ('orders', 'data', 'root'):
            assert response.code == 200
            assert response.data == {'test': "success"}
        else:
            assert response.code == 403
            assert not response.data


def test_request_permission_owners_read():
    """Request requiring OWNERS_READ permissions."""
    responses = helpers.make_request_all_roles('/api/developer/hello/OWNERS_READ', ret_json=True)
    for response in responses:
        if response.role in ('owners', 'data', 'root'):
            assert response.code == 200
            assert response.data == {'test': "success"}
        else:
            assert response.code == 403
            assert not response.data


def test_request_permission_user_management():
    """Request requiring USER_MANAGEMENT permissions."""
    responses = helpers.make_request_all_roles('/api/developer/hello/USER_MANAGEMENT', ret_json=True)
    for response in responses:
        if response.role in ('users', 'root'):
            assert response.code == 200
            assert response.data == {'test': "success"}
        else:
            assert response.code == 403
            assert not response.data


def test_request_permission_data_management():
    """Request requiring DATA_MANAGEMENT permissions."""
    responses = helpers.make_request_all_roles('/api/developer/hello/DATA_MANAGEMENT', ret_json=True)
    for response in responses:
        if response.role in ('data', 'root'):
            assert response.code == 200
            assert response.data == {'test': "success"}
        else:
            assert response.code == 403
            assert not response.data


def test_csrf():
    """Perform POST, PUT and DELETE requests to confirm that CSRF works correctly."""
    
    for method in ('POST', 'PATCH', 'PUT', 'DELETE'):
        responses = helpers.make_request_all_roles('/api/developer/csrftest',
                                                   method=method,
                                                   set_csrf=False,
                                                   ret_json=True)
        for response in responses:
            assert response.code == 400
            assert not response.data

        responses = helpers.make_request_all_roles('/api/developer/csrftest',
                                                   method=method,
                                                   ret_json=True)
        for response in responses:
            assert response.code == 200
            assert response.data == {'test': "success"}


def test_api_key_auth():
    """Request target with login requirment using an API key"""
    response = requests.get(helpers.BASE_URL + '/api/developer/loginhello',
                            headers={'X-API-Key': '0',
                                     'X-API-User': 'base::testers'})
    assert response.status_code == 200
    assert json.loads(response.text) == {'test': 'success'}
    response = requests.get(helpers.BASE_URL + '/api/developer/loginhello',
                            headers={'X-API-Key': '0',
                                     'X-API-User': 'root::testers'})
    assert response.status_code == 401
    assert not response.text
    response = requests.get(helpers.BASE_URL + '/api/developer/loginhello',
                            headers={'X-API-Key': 'asd',
                                     'X-API-User': 'root::testers'})
    assert response.status_code == 401
    assert not response.text
    response = requests.get(helpers.BASE_URL + '/api/developer/loginhello',
                            headers={'X-API-Key': '0',
                                     'X-API-User': 'asd'})
    assert response.status_code == 401
    assert not response.text
