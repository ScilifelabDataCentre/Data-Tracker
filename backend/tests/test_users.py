"""Tests for dataset requests."""
import json
import re
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
        assert len(response.data['user']) == 5
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



def test_add_user(use_db):
    """Add a user."""
    db = use_db

    indata = {'auth_id': 'user@added'}
    responses = make_request_all_roles(f'/api/user/',
                                       ret_json=True,
                                       method='POST',
                                       data=indata)
    for response in responses:
        if response.role in ('users', 'root'):
            assert response.code == 200
            assert '_id' in response.data
            new_user_info = db['users'].find_one({'_id': uuid.UUID(response.data['_id'])})
            assert indata['auth_id'] == new_user_info['auth_id']
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    indata = {'affiliation': 'Added University',
              'auth_id': 'user2@added',
              'name': 'Added name',
              'email': 'user2@added.se',
              'permissions': ['ORDERS_SELF']}
    session = requests.session()
    as_user(session, USERS['root'])
    response = make_request(session,
                            f'/api/user/',
                            ret_json=True,
                            method='POST',
                            data=indata)
    assert response.code == 200
    assert '_id' in response.data
    new_user_info = db['users'].find_one({'_id': uuid.UUID(response.data['_id'])})
    for key in indata:
        assert new_user_info[key] == indata[key]


def test_delete_user(use_db):
    """Test deleting users (added when testing to add users)"""
    db = use_db

    re_users = re.compile('@added')
    users = list(db['users'].find({'auth_id': re_users}, {'_id': 1}))

    session = requests.Session()
    i = 0
    while i < len(users):
        for role in USERS:
            as_user(session, USERS[role])
            response = make_request(session,
                                    f'/api/user/{users[i]["_id"]}/',
                                    method='DELETE')
            if role in ('users', 'root'):
                assert response.code == 200
                assert not response.data
                assert not db['users'].find_one({'_id': users[i]['_id']})
                assert db['logs'].find_one({'data._id': users[i]['_id'],
                                            'action': 'delete',
                                            'data_type': 'user'})
                i += 1
                if i >= len(users):
                    break
            elif role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data


def test_key_login():
    """Test API key login for all users"""
    session = requests.Session()
    as_user(session, None)
    for i, userid in enumerate(USERS):
        response = make_request(session,
                                '/api/user/login/apikey/',
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


def test_key_reset(use_db):
    """Test generation of new API keys"""
    db = use_db

    mod_user = {'auth_id': '--facility 18--'}
    mod_user_info = db.users.find_one(mod_user)

    session = requests.Session()
    for i, userid in enumerate(USERS):
        as_user(session, USERS[userid])
        response = make_request(session,
                                '/api/user/me/apikey/',
                                method='POST')
        if userid == 'no-login':
            assert response.code == 401
            assert not response.data
            continue

        assert response.code == 200
        new_key = response.data['key']
        response = make_request(session,
                                '/api/user/login/apikey/',
                                data = {'api-user': USERS[userid],
                                        'api-key': new_key},
                                method='POST')
        assert response.code == 200
        assert not response.data
        db.users.update_one({'auth_id': userid}, {'$set': {'api_salt': 'abc',
                                                           'api_key': str(i-1)}})

        response = make_request(session,
                                f'/api/user/{mod_user_info["_id"]}/apikey/',
                                method='POST')
        if userid not in ('users', 'root'):
            assert response.code == 403
            assert not response.data
        else:
            assert response.code == 200
            new_key = response.data['key']
            response = make_request(session,
                                    '/api/user/login/apikey/',
                                    data = {'api-user': mod_user['auth_id'],
                                            'api-key': new_key},
                                    method='POST')
            assert response.code == 200
            assert not response.data


def test_get_user_logs_permissions(use_db):
    """
    Get user logs.

    Assert that USER_MANAGEMENT or actual user is required.
    """
    db = use_db
    user_uuid = db['users'].find_one({'auth_id': USERS['base']}, {'_id': 1})['_id']
    responses = make_request_all_roles(f'/api/user/{user_uuid}/log/',
                                       ret_json=True)
    for response in responses:
        if response.role in ('base', 'users', 'root'):
            assert response.code == 200
            assert 'logs' in response.data
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_get_user_logs(use_db):
    """
    Request the logs for multiple users.

    Confirm that the logs contain only the intended fields.
    """
    session = requests.session()
    db = use_db
    users = db['users'].aggregate([{'$sample': {'size': 2}}])
    for user in users:
        logs = list(db['logs'].find({'data_type': 'user', 'data._id': user['_id']}))
        as_user(session, USERS['users'])
        response = make_request(session, f'/api/user/{user["_id"]}/log/', ret_json=True)
        assert response.data['dataType'] == 'user'
        assert response.data['entryId'] == str(user['_id'])
        assert len(response.data['logs']) == len(logs)
        assert response.code == 200


def test_get_current_user_logs(use_db):
    """
    Get current user logs.

    Should return logs for all logged in users.
    """
    db = use_db
    responses = make_request_all_roles(f'/api/user/me/log/',
                                       ret_json=True)
    for response in responses:
        if response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 200
            assert 'logs' in response.data


def test_get_user_actions_access(use_db):
    """
    Get user logs.

    Assert that USER_MANAGEMENT or actual user is required.
    """
    db = use_db
    user_uuid = db['users'].find_one({'auth_id': USERS['base']}, {'_id': 1})['_id']
    responses = make_request_all_roles(f'/api/user/{user_uuid}/actions/',
                                       ret_json=True)
    for response in responses:
        if response.role in ('base', 'users', 'root'):
            assert response.code == 200
            assert 'logs' in response.data
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_get_current_user_actions(use_db):
    """
    Get current user logs.

    Should return logs for all logged in users.
    """
    db = use_db
    responses = make_request_all_roles(f'/api/user/me/actions/',
                                       ret_json=True)
    for response in responses:
        if response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 200
            assert 'logs' in response.data
