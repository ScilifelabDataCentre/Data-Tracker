"""Helper functions for tests, including requests to e.g. change current user."""

import collections
import datetime
import json
import os
import random
import string

import pytest
import requests

import config
import structure
import utils


CURR_DIR = os.path.realpath(__file__)
SETTINGS = json.loads(open(f'{os.path.dirname(CURR_DIR)}/settings_tests.json').read())
BASE_URL = f'{SETTINGS["host"]}:{SETTINGS["port"]}'

TEST_LABEL = {'extra': {'testing': 'yes'}}

USERS = {'no-login': None,
         'base': 'base@testers',
         'orders': 'orders@testers',
         'owners': 'owners@testers',
         'users': 'users@testers',
         'data': 'data@testers',
         'doi': 'doi@testers',
         'root': 'root@testers'}

Response = collections.namedtuple('Response',
                                  ['data', 'code', 'role'],
                                  defaults=[None, None, None])


def db_connection():
    """Get a connection to the db as defined in the app config."""
    conf = config.init()
    client = utils.get_dbclient(conf)
    return utils.get_db(client, conf)


@pytest.fixture
def use_db():
    """Get a connection to the db as defined in the app config."""
    conf = config.init()
    client = utils.get_dbclient(conf)
    db = utils.get_db(client, conf)
    yield db
    client.close()


def as_user(session: requests.Session, auth_id: str, set_csrf: bool = True) -> int:
    """
    Helper method to log in as requested user.

    Session changed in-place.

    Args:
        session (requests.Session): The session to update.
        auth_id (str): The auth id of the user.

    Returns:
        int: Status code.
    """
    if auth_id:
        code = session.get(f'{BASE_URL}/api/developer/login/{auth_id}').status_code
        assert code == 200
    else:
        code = session.get(f'{BASE_URL}/api/user/logout').status_code
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
    db = db_connection()
    # prepare
    order_indata = structure.order()
    order_indata.update({'links': [{'description': 'Test description', 'url': 'http://test_url'}],
                         'description': 'Added by fixture.',
                         'title': 'Test title from fixture'})
    order_indata.update(TEST_LABEL)
    session = requests.Session()
    as_user(session, USERS['orders'])
    data_user = db['users'].find_one({'auth_id': USERS['data']})
    order_indata.update({'creator': data_user['_id']})
    order_indata.update({'receiver': data_user['_id']})
    
    dataset_indata = structure.dataset()
    db['datasets'].insert_one(dataset_indata)
    order_indata['datasets'].append(dataset_indata['_id'])
    db['orders'].insert_one(order_indata)
    yield dataset_indata['_id']

    # cleanup
    db['orders'].delete_one({'_id': order_indata['_id']})
    db['datasets'].delete_one({'_id': dataset_indata['_id']})


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
    elif method == 'PATCH':
        response = session.patch(f'{BASE_URL}{url}',
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
    return Response(data=data, code=response.status_code)


def make_request_all_roles(url: str, method: str = 'GET', data=None,
                           set_csrf: bool = True, ret_json: bool = False) -> list:
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
        req = make_request(session, url, data, method, ret_json)
        responses.append(Response(data=req.data, code=req.code, role=user))
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
