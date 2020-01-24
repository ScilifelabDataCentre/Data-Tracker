"""Tests for project requests."""
import json
import time
import uuid
import requests

from helpers import make_request, as_user, make_request_all_roles, project_for_tests, USERS, random_string, parse_time
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


def test_user_projects():
    """
    Retrieve a list of projects belonging to current user.

    Confirm that they actually belong to the user.
    """
    # wait for queries to be ready
    return
    session = requests.Session()
    for _ in range(3):
        response = make_request(session, '/api/project/random')
        expected_projects = response[0]['projects'][0]['projects']
        as_user(session, response[0]['projects'][0]['owner'])
        responses = make_request_all_roles('/api/project/user')
        assert [response[1] for response in responses] == [401, 200, 200, 200]
        for response in responses:
            if response[1] == 401:
                assert not response[0]
            print(response[0])
            projects = [doc['uuid'] for doc in json.loads(response[0])['projects']]
            assert projects == expected_projects


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
    responses = make_request_all_roles(f'/api/project/{orig["uuid"]}')
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
        response = make_request(session, f'/api/project/{orig["uuid"]}')
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
