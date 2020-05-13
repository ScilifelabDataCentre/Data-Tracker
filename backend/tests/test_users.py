"""Tests for dataset requests."""
import json
import requests
import uuid

from helpers import make_request, as_user, make_request_all_roles, USERS, use_db, random_string
# pylint: disable=redefined-outer-name

def test_logout():
    """Assure that session is cleared after logging out."""
    session = requests.Session()
    as_user(session, USERS['root'])
    response = make_request(session, '/api/user/me/')
    for field in response.data['user']:
        assert response.data['user'][field]
    response = make_request(session, '/api/user/logout', ret_json=False)
    response = make_request(session, '/api/user/me/')
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
    """Retrieve info about current user."""
    responses = make_request_all_roles('/api/user/me/',
                                       ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['user']) == 4
        if response.role != 'no-login':
            assert response.data['user']['name'] == f'{response.role.capitalize()} Test'


def test_update_current_user(use_db):
    """Update the info about the current user."""
    db = use_db
    session = requests.Session()

    indata = {}
    for user in USERS:
        as_user(session, USERS[user])
        user_info = db['users'].find_one({'auth_id': USERS[user]})
        response = make_request(session,
                                '/api/user/me/',
                                ret_json=True,
                                method='PATCH',
                                data=indata)
        if user != 'no-login':
            assert response.code == 200
        else:
            assert response.code == 401
        assert not response.data
        new_user_info = db['users'].find_one({'auth_id': USERS[user]})
        assert user_info == new_user_info

    indata = {'affiliation': 'Updated University',
              'name': 'Updated name'}
    session = requests.Session()
    for user in USERS:
        as_user(session, USERS[user])
        user_info = db['users'].find_one({'auth_id': USERS[user]})
        response = make_request(session,
                                '/api/user/me/',
                                ret_json=True,
                                method='PATCH',
                                data=indata)
        if user != 'no-login':
            assert response.code == 200
            assert not response.data
            new_user_info = db['users'].find_one({'auth_id': USERS[user]})
            for key in new_user_info:
                if key in indata.keys():
                    assert new_user_info[key] == indata[key]
                else:
                    user_info[key] == new_user_info[key]
                    db['users'].update_one(new_user_info, {'$set': user_info})
        else:
            assert response.code == 401
            assert not response.data


def test_update_current_user_bad():
    """Update the info about the current user."""
    session = requests.Session()
    indata = {'_id': str(uuid.uuid4())}
    responses = make_request_all_roles('/api/user/me/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {'api_key': uuid.uuid4().hex}
    responses = make_request_all_roles('/api/user/me/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {'auth_id': uuid.uuid4().hex}
    responses = make_request_all_roles('/api/user/me/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {'email': 'email@example.com'}
    responses = make_request_all_roles('/api/user/me/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {'permissions': ['USER_MANAGEMENT', 'DATA_MANAGEMENT']}
    responses = make_request_all_roles('/api/user/me/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data


def test_update_user(use_db):
    """Update the info for a user."""
    db = use_db

    user_info = db['users'].find_one({'auth_id': USERS['base']})
    
    indata = {}
    responses = make_request_all_roles(f'/api/user/{user_info["_id"]}/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role in ('users', 'root'):
            assert response.code == 200
            new_user_info = db['users'].find_one({'auth_id': user_info['auth_id']})
            assert user_info == new_user_info
        elif response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {'affiliation': 'Updated University',
              'name': 'Updated name'}
    session = requests.session()
    for user_type in USERS:
        as_user(session, USERS[user_type])
        response = make_request(session,
                                f'/api/user/{user_info["_id"]}/',
                                ret_json=True,
                                method='PATCH',
                                data=indata)
        if user_type in ('users', 'root'):
            assert response.code == 200
            assert not response.data
            new_user_info = db['users'].find_one({'auth_id': user_info['auth_id']})
            for key in indata:
                assert new_user_info[key] == indata[key]
            db['users'].update_one(new_user_info, {'$set': user_info})
        elif user_type == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_update_user_bad(use_db):
    """
    Update the info for a user.

    Bad requests.
    """
    db = use_db
    user_info = db['users'].find_one({'auth_id': USERS['base']})

    session = requests.Session()
    indata = {'_id': str(uuid.uuid4())}
    responses = make_request_all_roles(f'/api/user/{user_info["_id"]}/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {'api_key': uuid.uuid4().hex}
    responses = make_request_all_roles(f'/api/user/{user_info["_id"]}/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {'email': 'bad@email'}
    responses = make_request_all_roles(f'/api/user/{user_info["_id"]}/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role in ('users', 'root'):
            assert response.code == 400
        elif response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {}
    responses = make_request_all_roles(f'/api/user/{uuid.uuid4()}/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role in ('users', 'root'):
            assert response.code == 404
        elif response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {}
    responses = make_request_all_roles(f'/api/user/{random_string()}/',
                                       ret_json=True,
                                       method='PATCH',
                                       data=indata)
    for response in responses:
        if response.role in ('users', 'root'):
            assert response.code == 404
        elif response.role == 'no-login':
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data
