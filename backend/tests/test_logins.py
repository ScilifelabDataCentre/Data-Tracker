"""Tests for logins."""
import json
import re
import requests
import uuid

import helpers

from helpers import make_request, as_user, make_request_all_roles, USERS, use_db, random_string
# pylint: disable=redefined-outer-name

def test_logout():
    """Assure that session is cleared after logging out."""
    session = requests.Session()
    as_user(session, USERS['root'])
    response = make_request(session, '/api/user/me/')
    for field in response.data['user']:
        assert response.data['user'][field]
    response = make_request(session, '/api/logout/', ret_json=False)
    response = make_request(session, '/api/user/me/')
    for field in response.data['user']:
        assert not response.data['user'][field]


def test_key_login():
    """Test API key login for all users"""
    session = requests.Session()
    as_user(session, None)
    for i, userid in enumerate(USERS):
        response = make_request(session,
                                '/api/login/apikey/',
                                data = {'api-user': USERS[userid],
                                        'api-key': str(i-1)},
                                method='POST')
        if userid == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 200
            assert not response.data

            response = make_request(session,
                                    '/api/developer/loginhello')
            assert response.code == 200
            assert response.data == {'test': 'success'}


def test_list_login_types():
    """List possible ways to login"""
    responses = helpers.make_request_all_roles('/api/login/', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert response.data == {'types': ['apikey', 'oidc']}


def test_list_oidc_types():
    """List supported oidc logins"""
    responses = helpers.make_request_all_roles('/api/login/oidc/', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert response.data == {'oidc server': '/api/login/oidc/oidcserver'}
