"""Tests for project requests."""
import json
import uuid
import requests

from helpers import make_request, as_user, make_request_all_roles,\
    USERS, random_string, use_db
# pylint: disable=redefined-outer-name

def test_list_projects():
    """
    Request a list of all projects.

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles('/api/project/', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['projects']) == 500


def test_random_project():
    """Request a random project."""
    responses = make_request_all_roles('/api/project/random', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['projects']) == 1


def test_random_projects():
    """Request random projects."""
    session = requests.Session()
    as_user(session, USERS['base'])
    for i in (1, 5, 0):
        response = make_request(session, f'/api/project/random/{i}', ret_json=True)
        assert response.code == 200
        assert len(response.data['projects']) == i

    response = make_request(session, '/api/project/random/-1')
    assert response[1] == 404
    assert not response[0]


def test_get_project_permissions(use_db):
    """Test permissions for requesting a project."""
    db = use_db
    project = list(db['projects'].aggregate([{'$sample': {'size': 1}}]))[0]

    responses = make_request_all_roles(f'/api/project/{project["_id"]}', ret_json=True)
    for response in responses:
        assert response.code == 200


def test_get_project(use_db):
    """
    Request multiple projects by uuid, one at a time.

    Projects are choosen randomly using /api/project/random.
    """
    db = use_db
    session = requests.Session()
    for _ in range(10):
        project = list(db['projects'].aggregate([{'$sample': {'size': 1}}]))[0]
        print(project)
        project['_id'] = str(project['_id'])
        project['owners'] = [str(entry) for entry in project['owners']]
        project['datasets'] = [str(entry) for entry in project['datasets']]
        response = make_request(session, f'/api/project/{project["_id"]}')
        assert response.code == 200
        for field in project:
            assert project[field] == response.data['project'][field]


def test_get_project_bad():
    """
    Request projects using bad identifiers.

    All are expected to return 404.
    """
    session = requests.Session()
    for _ in range(2):
        response = make_request(session, f'/api/project/{uuid.uuid4().hex}')
        assert response.code == 404
        assert not response.data

    for _ in range(2):
        response = make_request(session, f'/api/project/{random_string()}')
        assert response.code == 404
        assert not response.data
