import json
import os
import requests

import pytest


CURR_DIR = os.path.realpath(__file__)
SETTINGS = json.loads(open(f'{os.path.dirname(CURR_DIR)}/settings_tests.json').read())
BASE_URL = f'{SETTINGS["host"]}:{SETTINGS["port"]}'

USERS = {'no-login': None,
         'user': 'user@example.com',
         'steward': 'steward@example.com',
         'admin': 'admin@example.com'}


def make_request_all_roles(url: str, method='GET', payload=None) -> list:
    """
    Perform a query for all roles (anonymous, User, Steward, Admin).

    Args:
        url (str): the url to query

    Returns:
        list: the results of the performed queries

    """
    responses = []
    session = requests.Session()
    for user in USERS:
        as_user(session, USERS[user])
        responses.append(make_request(session, url, payload, method, ret_json=False))
    return responses


def as_user(session: requests.Session, username: str) -> int:
    """
    Helper method to log in as requested user.

    Session changed in-place.

    Args:
        session (requests.Session): the session to uodate
        username (str): the id of the user, 0 means log out

    Returns:
        int: status_code
    """
    if username:
        code = session.get(f'{BASE_URL}/api/developer/login/{username}').status_code
        assert code == 200
    else:
        code = session.get(f'{BASE_URL}/api/user/logout').status_code
        assert code == 200
        session.get(f'{BASE_URL}/api/developer/hello')  # reset cookies
    return code


@pytest.fixture
def dataset_for_tests():
    # prepare
    session = requests.Session()
    as_user(session, 5)
    payload = {'dataset': {'title': 'A Unique Title',
                           'description': 'Description',
                           'doi': 'DOI',
                           'creator': 'Creator',
                           'dmp': 'Data Management Plan',
                           'publications': [{'identifier': 'Publication'}],
                           'dataUrls': [{'url': 'Data Access URL', 'description': 'Description'}],
                           'projects': [2]}}

    data, status_code = make_request(session,
                                  '/api/dataset/add',
                                  payload)
    assert status_code == 200
    ds_id = data['id']

    yield ds_id

    # cleanup
    payload = {'id': ds_id}
    print(payload)
    _, status_code = make_request(session,
                                  '/api/dataset/delete',
                                  payload)


def make_request(session, url: str, data: dict = None, method='GET', ret_json:bool = True) -> dict:
    """
    Helper method for using get/post to a url.

    Args:
        session (requests.Session()): The session to use
        url: str: The url to get without {BASE_URL} prefix (but with leading /)
        data (dict): The payload data
        method (str): HTTP method to use
        ret_json (bool): Should json.loads(response.text) be the response?

    Returns:
        tuple: (data: dict, status_code: int)

    """
    if method == 'GET':
        response = session.get(f'{BASE_URL}{url}')
    elif method == 'POST':
        response = session.post(f'{BASE_URL}{url}',
                                data=json.dumps(data))
    elif method == 'PUT':
        response = session.put(f'{BASE_URL}{url}',
                               data=json.dumps(data))
    elif method == 'DELETE':
        response = session.delete(f'{BASE_URL}{url}')
    else:
        raise ValueError(f'Unsupported http method ({method})')

    if response.text and ret_json:
        data = json.loads(response.text)
    elif response.text:
        data = response.text
    else:
        data = ''
    return (data, response.status_code)


@pytest.fixture
def project_for_tests():
    # prepare
    session = requests.Session()
    as_user(session, 5)
    payload = {'project': {'title': 'A Unique Title for a Project',
                           'description': 'Description for a project.',
                           'creator': 'Creator'}}

    data, status_code = make_request(session,
                                  '/api/project/add',
                                  payload)
    assert status_code == 200

    proj_id = data['id']
    print(proj_id)
    yield proj_id

    # cleanup
    payload = {'id': proj_id}
    make_request(session,
                 '/api/dataset/delete',
                 payload)
