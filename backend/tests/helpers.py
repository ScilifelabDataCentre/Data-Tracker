"""Helper functions for tests, including requests to e.g. change current user."""

import datetime
import json
import os
import random
import string

import pytest
import requests


CURR_DIR = os.path.realpath(__file__)
SETTINGS = json.loads(open(f'{os.path.dirname(CURR_DIR)}/settings_tests.json').read())
BASE_URL = f'{SETTINGS["host"]}:{SETTINGS["port"]}'

USERS = {'no-login': None,
         'user': 'user@example.com',
         'steward': 'steward@example.com',
         'admin': 'admin@example.com'}


def as_user(session: requests.Session, username: str, set_csrf: bool = True) -> int:
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
    if set_csrf:
        session.headers['X-CSRFToken'] = session.cookies.get('_csrf_token')
    return code


@pytest.fixture
def dataset_for_tests():
    """
    Add a new dataset that can be modified in tests, followed by automatic removal.

    Yields the uuid of the added dataset.
    """

    # prepare
    indata = {'links': [{'description': 'Test description', 'url': 'http://test_url'}],
              'description': 'Test description',
              'title': 'Test title'}
    session = requests.Session()
    as_user(session, USERS['steward'])

    data, status_code = make_request(session,
                                     '/api/dataset/add',
                                     data=indata,
                                     method='POST')
    assert status_code == 200
    uuid = data['_id']

    yield uuid

    # cleanup
    _, status_code = make_request(session,
                                  f'/api/dataset/{uuid}',
                                  method='DELETE')


def make_request(session, url: str, data: dict = None, method='GET', ret_json: bool = True) -> dict:
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
        data = None
    return (data, response.status_code)


def make_request_all_roles(url: str, method: str = 'GET', data=None, set_csrf: bool = True) -> list:
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
        as_user(session, USERS[user], set_csrf=set_csrf)
        responses.append(make_request(session, url, data, method, ret_json=False))
    return responses


@pytest.fixture
def project_for_tests():
    """
    Add a new project that can be modified in tests and then removed.

    Yields the uuid of the added project.
    """
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

    proj_id = data['_id']
    yield proj_id

    # cleanup
    payload = {'_id': proj_id}
    make_request(session,
                 '/api/project/delete',
                 payload)


def random_string(min_length: int = 1, max_length: int = 150):
    """
    Generate a random string.

    Args:
        min_length(int): minimum length of the generated string
        max_length(int): maximum length of the generated string

    Returns:
        str: a string of random characters

    """
    char_source = string.ascii_letters + string.digits + '-'
    length = random.randint(min_length, max_length)
    return ''.join(random.choice(char_source) for _ in range(length))


def parse_time(datetime_str: str):
    """
    Parse the timestamp from a query.

    Args:
        datetime_str (str): timestamp string (Wed, 22 Jan 2020 21:07:35 GMT)
    """
    str_format = '%a, %d %b %Y %H:%M:%S %Z'
    return datetime.datetime.strptime(datetime_str, str_format)
