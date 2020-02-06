"""Tests for project requests."""
import json
import uuid
import requests

from helpers import make_request, as_user, make_request_all_roles,\
    USERS, random_string
# pylint: disable=redefined-outer-name

def test_list_projects():
    """
    Request a list of all projects.

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles('/api/project/all')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    for response in responses:
        assert len(json.loads(response[0])['projects']) == 500


def test_random_project():
    """Request a random project."""
    responses = make_request_all_roles('/api/project/random')
    assert [response[1] for response in responses] == [200, 200, 200, 200]
    for response in responses:
        assert len(json.loads(response[0])['projects']) == 1


def test_random_projects():
    """Request random projects."""
    session = requests.Session()
    as_user(session, USERS['user'])
    for i in (1, 5, 0):
        response = make_request(session, f'/api/project/random/{i}')
        assert response[1] == 200
        assert len(response[0]['projects']) == i

    response = make_request(session, '/api/project/random/-1')
    assert response[1] == 404
    assert not response[0]


def test_get_project_permissions():
    """Test permissions for requesting a project."""
    session = requests.Session()
    orig = make_request(session, '/api/project/random')[0]['projects'][0]
    responses = make_request_all_roles(f'/api/project/{orig["_id"]}')
    for response in responses:
        assert json.loads(response[0])['project'] == orig
        assert response[1] == 200


def test_get_project():
    """
    Request multiple projects by uuid, one at a time.

    Projects are choosen randomly using /api/project/random.
    """
    session = requests.Session()
    for _ in range(10):
        orig = make_request(session, '/api/project/random')[0]['projects'][0]
        response = make_request(session, f'/api/project/{orig["_id"]}')
        assert response[1] == 200
        requested = response[0]['project']
        assert orig == requested


def test_get_project_bad():
    """
    Request projects using bad identifiers.

    All are expected to return 404.
    """
    session = requests.Session()
    for _ in range(5):
        response = make_request(session, f'/api/project/{uuid.uuid4().hex}')
        assert response == (None, 404)

    for _ in range(5):
        response = make_request(session, f'/api/project/{random_string()}')
        assert response == (None, 404)


def test_add_get():
    """
    Request data structure for .get(project/add).

    Should require at least Steward.
    """
    expected_success = {'contact': '',
                        'datasets': [],
                        'description': '',
                        'dmp': '',
                        'owner': '',
                        'publications': [],
                        'title': ''}

    responses = make_request_all_roles('/api/project/add')
    assert [response[1] for response in responses] == [401, 401, 200, 200]
    assert [json.loads(response[0]) if response[0] else None
            for response in responses] == [None,
                                           None,
                                           expected_success,
                                           expected_success]
