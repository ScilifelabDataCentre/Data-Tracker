import json
import os
import requests

import pytest


CURR_DIR = os.path.realpath(__file__)
SETTINGS = json.loads(open(f'{os.path.dirname(CURR_DIR)}/settings_tests.json').read())
BASE_URL = f'{SETTINGS["host"]}:{SETTINGS["port"]}'

def as_user(session, user_id: int) -> int:
    """
    Helper method to log in as requested user.

    Session changed in-place.

    Args:
        session: a requests.Session()
        user_id: the id of the user, 0 means log out

    Returns:
        int: status_code
    """
    if user_id != 0:
        code = session.get(f'{BASE_URL}/developer/login?userid={user_id}').status_code
        assert code == 200
        session.headers['X-Xsrftoken'] = session.cookies['_xsrf']
    else:
        code = session.get(f'{BASE_URL}/logout').status_code
        session.get(f'{BASE_URL}/api/datasets')  # reset cookies
        session.headers['X-Xsrftoken'] = session.cookies['_xsrf']
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
                           'tags': [{'title': 'Tag1'}, {'title': 'Tag2'}],
                           'publications': [{'identifier': 'Publication'}],
                           'dataUrls': [{'url': 'Data Access URL', 'description': 'Description'}],
                           'projects': [2]}}

    _, status_code = make_request(session,
                                  '/api/dataset/add',
                                  payload)
    assert status_code == 200

    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     {'query': {'title': 'A Unique Title'}})
    assert status_code == 200

    ds_id = data['datasets'][0]['id']

    yield ds_id

    # cleanup
    payload = {'identifier': ds_id}
    make_request(session,
                 '/api/dataset/delete',
                 payload)


def make_request(session, url: str, data: dict = None) -> dict:
    """
    Helper method for using get/post to a url.

    Args:
        session: A requests.Session()
        url: The url to get without {BASE_URL} prefix (but with leading /)
        data: The data to POST; no data means GET

    Returns:
        tuple: (data: dict, status_code: int)
    """
    if data:
        response = session.post(f'{BASE_URL}{url}',
                                data=json.dumps(data))
    else:
        response = session.get(f'{BASE_URL}{url}')

    if response.text:
        data = json.loads(response.text)
    else:
        data = {}
    return (data, response.status_code)


@pytest.fixture
def project_for_tests():
    # prepare
    session = requests.Session()
    as_user(session, 5)
    payload = {'project': {'title': 'A Unique Title for a Project',
                           'description': 'Description for a project.',
                           'creator': 'Creator'}}

    _, status_code = make_request(session,
                                  '/api/project/add',
                                  payload)
    assert status_code == 200

    data, status_code = make_request(session,
                                     '/api/project/query',
                                     {'query': {'title': 'A Unique Title'}})
    assert status_code == 200

    ds_id = data['datasets'][0]['id']

    yield ds_id

    # cleanup
    payload = {'identifier': ds_id}
    make_request(session,
                 '/api/dataset/delete',
                 payload)
