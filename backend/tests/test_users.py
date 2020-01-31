"""Tests for dataset requests."""
import json
import requests

from helpers import make_request, as_user, make_request_all_roles, USERS
# pylint: disable=redefined-outer-name

def test_logout():
    """Assure that session is stopped after logging out."""
    session = requests.Session()
    as_user(session, USERS['user'])
    response = make_request(session, '/api/developer/loginhello')
    assert response == ({'test': 'success'}, 200)
    response = make_request(session, '/api/user/logout', ret_json=False)
    assert response[1] == 200

    response = make_request(session, '/api/developer/loginhello', ret_json=False)
    assert response == (None, 401)


def test_list_users():
    """
    Retrieve list of users.

    Assert that admin is required.
    """
    responses = make_request_all_roles('/api/user/all')
    assert [response[1] for response in responses] == [401, 401, 401, 200]
    for response in responses:
        if response[1] == 401:
            assert response[0] is None
        else:
            data = json.loads(response[0])
            assert len(data['users']) == 100


def test_list_info():
    """
    Retrieve info about current user.
    """
    responses = make_request_all_roles('/api/user/me')
    assert [response[1] for response in responses] == [200]*4
    for i, response in enumerate(responses):
        data = json.loads(response[0])
        assert len(data['user']) == 5
        if i == 0:
            for field in data['user']:
                assert not data['user'][field]
        else:
            for field in data['user']:
                assert data['user'][field]
