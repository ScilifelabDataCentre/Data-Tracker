"""Tests for the project handlers."""

import requests

from helpers import as_user, make_request, project_for_tests


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

    payload = {'project': {'title': 'Added Project Title1',
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
    print(f"/api/project/{data['id']}/delete")
    _, status_code = make_request(session, f"/api/project/{data['id']}/delete")
    assert status_code == 200

    as_user(session, 6)
    payload['title'] = 'Added Project Title2'
    data, status_code = make_request(session,
                                     '/api/project/add',
                                     payload)
    assert status_code == 200
    assert 'id' in data
    print(f"/api/project/{data['id']}/delete")
    _, status_code = make_request(session, f"/api/project/{data['id']}/delete")
    assert status_code == 200

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


def test_delete_project_get(project_for_tests):
    """Test DeleteProject.get()"""
    session = requests.Session()
    expected = {'id': 9876543210}

    # not logged in/normal user
    for user in (0, 1):
        as_user(session, user)
        data, status_code = make_request(session, '/api/project/delete')
        assert status_code == 403
        assert not data
        data, status_code = make_request(session, '/api/project/4/delete')
        assert status_code == 403
        assert not data

    # steward
    as_user(session, 5)
    data, status_code = make_request(session, '/api/project/delete')
    assert status_code == 200
    assert data == expected
    data, status_code = make_request(session, f'/api/project/{project_for_tests}/delete')
    assert status_code == 200
    assert not data

    # admin
    as_user(session, 6)
    data, status_code = make_request(session, '/api/project/delete')
    assert status_code == 200
    data, status_code = make_request(session, f'/api/project/{project_for_tests}/delete')
    assert status_code == 400
    assert not data


def test_delete_project_post(project_for_tests):
    """Test DeleteProject.post()"""
    session = requests.Session()

    add_payload = {'project': {'title': 'An added Project',
                               'description': 'Description'}}

    # steward
    as_user(session, 5)
    data, status_code = make_request(session,
                                     '/api/project/add',
                                     add_payload)
    assert status_code == 200
    payload = {'id': data['id']}
    data, status_code = make_request(session,
                                     '/api/project/delete',
                                     payload)
    assert status_code == 200
    assert not data

    # admin
    as_user(session, 6)
    data, status_code = make_request(session,
                                     '/api/project/add',
                                     add_payload)
    assert status_code == 200
    payload = {'id': data['id']}
    data, status_code = make_request(session,
                                     '/api/project/delete',
                                     payload)
    assert status_code == 200
    assert not data

    payload = {'identifier': 9876543210}
    data, status_code = make_request(session,
                                     f'/api/project/{project_for_tests}/delete',
                                     payload)
    assert status_code == 200
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
