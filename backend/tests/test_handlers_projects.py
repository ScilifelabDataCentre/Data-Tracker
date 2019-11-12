"""Tests for the project handlers."""

import requests

from helpers import as_user, make_request


def test_add_project_get():
    """Test AddProject.get()"""
    session = requests.Session()

    as_user(session, 0)
    data, status_code = make_request(session, '/api/project/add')
    assert status_code == 403
    assert not data

    as_user(session, 1)
    data, status_code = make_request(session, '/api/project/add')
    assert status_code == 403
    assert not data

    as_user(session, 5)
    data, status_code = make_request(session, '/api/project/add')
    assert status_code == 200
    assert data.get('project')
    assert len(data['project']) == 4

    as_user(session, 6)
    data, status_code = make_request(session, '/api/project/add')
    assert status_code == 200
    assert data.get('project')
    assert len(data['project']) == 4


def test_add_project_post():
    """Test AddProject.get()"""
    session = requests.Session()

    payload = {'project': {'title': 'Project Title',
                           'description': 'Description for the project.',
                           'creator': 'Creator of project'}}
    
    as_user(session, 0)
    data, status_code = make_request(session,
                                     '/api/project/add',
                                     payload)
    assert status_code == 403
    assert not data

    as_user(session, 1)
    data, status_code = make_request(session,
                                     '/api/project/add',
                                     payload)
    assert status_code == 403
    assert not data

    as_user(session, 5)
    data, status_code = make_request(session,
                                     '/api/project/add',
                                     payload)
    assert status_code == 200
    assert 'id' in data
    
    as_user(session, 6)
    data, status_code = make_request(session,
                                     '/api/project/add',
                                     payload)
    assert status_code == 200
    assert 'id' in data

    # failing requests
    as_user(session, 5)
    data, status_code = make_request(session,
                                     '/api/project/add',
                                     {'stuff': 'value'})
    assert status_code == 400
    assert not data

    data, status_code = make_request(session,
                                     '/api/project/add',
                                     {'project': {'title':''}})
    assert status_code == 400
    assert not data
    data, status_code = make_request(session,
                                     '/api/project/add',
                                     {'project': {'description':'Some text.'}})
    assert status_code == 400
    assert not data
    

def test_get_project_get():
    """Test GetProject.get()"""
    session = requests.Session()
    as_user(session, 0)
    data, status_code = make_request(session, '/api/project/1')
    assert status_code == 200
    assert len(data) == 5
    assert data['title'] == f"Project title {data['id']}"

    as_user(session, 1)
    data, status_code = make_request(session, '/api/project/1')
    assert status_code == 200
    assert len(data) == 5
    assert data['title'] == f"Project title {data['id']}"

    as_user(session, 5)
    data, status_code = make_request(session, '/api/project/1')
    assert status_code == 200
    assert len(data) == 5
    assert data['title'] == f"Project title {data['id']}"

    as_user(session, 6)
    data, status_code = make_request(session, '/api/project/1')
    assert status_code == 200
    assert len(data) == 5
    assert data['title'] == f"Project title {data['id']}"


def test_list_projects_get():
    """Test ListProjects.get()"""
    session = requests.Session()
    as_user(session, 0)
    data, status_code = make_request(session, '/api/projects')
    assert status_code == 200
    assert len(data['projects']) == 6
    assert data['projects'][0]['title'] == f"Project title {data['projects'][0]['id']}"


def test_update_project_post():
    """Test UpdateProject.post()"""
    session = requests.Session()
    as_user(session, 0)

    proj_id = 1
    payload = {'id': 1, 'title': 'New title'}
    data, status_code = make_request(session,
                                     f'/api/project/{proj_id}/update',
                                     payload)
    assert status_code == 403
    assert not data
