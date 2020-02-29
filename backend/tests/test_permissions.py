"""Tests for permission levels."""

import json

import helpers

# pylint: disable=redefined-outer-name


def test_request_no_permissions_required():
    """Request target with no permission requirements."""
    responses = helpers.make_request_all_roles('/api/developer/hello', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert response.data == {'test': "success"}


def test_request_login_required():
    """Request target with no permission requirements."""
    responses = helpers.make_request_all_roles('/api/developer/loginhello', ret_json=True)
    for response in responses:
        if response.role != 'no-login':
            assert response.code == 200
            assert response.data == {'test': "success"}
        else:
            assert response.code == 401
            assert not response.data


def test_request_permission_orders_self():
    """Request requiring ORDERS_SELF permissions."""
    responses = helpers.make_request_all_roles('/api/developer/hello/ORDERS_SELF', ret_json=True)
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


def test_request_permission_doi_reviewer():
    """Request target with no login requirement."""
    responses = helpers.make_request_all_roles('/api/developer/hello/DOI_REVIEWER', ret_json=True)
    for response in responses:
        if response.role in ('doi', 'root'):
            assert response.code == 200
            assert response.data == {'test': "success"}
        else:
            assert response.code == 403
            assert not response.data


def test_csrf():
    """Perform POST, PUT and DELETE requests to confirm that CSRF works correctly."""
    
    for method in ('POST', 'PUT', 'DELETE'):
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
