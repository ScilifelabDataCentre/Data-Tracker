"""Tests for project requests."""
import json
import uuid
import requests

from helpers import make_request, as_user, make_request_all_roles,\
    USERS, random_string, use_db, TEST_LABEL
# pylint: disable=redefined-outer-name

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


def test_add_project_permissions(use_db):
    """
    Add a project.

    Test permissions.
    """
    db = use_db
    
    indata = {'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/project/',
                                       method='POST',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 200
            assert '_id' in response.data
            assert len(response.data['_id']) == 36

    user_info = db['users'].find_one({'auth_id': USERS['base']})
    indata.update({'owners': [str(user_info['_id'])]})

    responses = make_request_all_roles(f'/api/project/',
                                       method='POST',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('base', 'data', 'root'):
            assert response.code == 200
            assert '_id' in response.data
            assert len(response.data['_id']) == 36
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 400
            assert not response.data

    dataset_info = next(db['datasets'].aggregate([{'$sample': {'size': 1}}]))
    order_info = db['orders'].find_one({'datasets': dataset_info['_id']})
    user_info = db['users'].find_one({'_id': order_info['creator']})
    indata.update({'owners': [str(user_info['_id'])],
                   'datasets': [str(dataset_info['_id'])]})

    session = requests.Session()
    as_user(session, user_info['api_key'])
    response = make_request(session,
                            f'/api/project/',
                            method='POST',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    assert '_id' in response.data
    assert len(response.data['_id']) == 36
    
    responses = make_request_all_roles(f'/api/project/',
                                       method='POST',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('data', 'root'):
            assert response.code == 200
            assert '_id' in response.data
            assert len(response.data['_id']) == 36
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 400
            assert not response.data
    
    


def test_add_project(use_db):
    """
    Add a project.

    Confirm that fields are set correctly.
    """
    db = use_db

    dataset_info = next(db['datasets'].aggregate([{'$sample': {'size': 1}}]))
    order_info = db['orders'].find_one({'datasets': dataset_info['_id']})
    session = requests.Session()
    user_info = db['users'].find_one({'_id': order_info['receiver']})

    as_user(session, user_info['api_key'])
    
    indata = {'description': 'Test description',
              'contact': 'user@example.com',
              'dmp': 'https://dmp_url_test',
              'owners': [str(user_info['_id'])],
              'publications': [{'title': 'A test publication title',
                                'doi': 'doi://a_test_doi_value'}],
              'title': 'Test title',
              'datasets': [dataset]}
    indata.update(TEST_LABEL)

    response = make_request(session,
                            f'/api/project/',
                            method='POST',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    assert '_id' in response.data
    assert len(response.data['_id']) == 36
    project = db['projects'].find_one({'_id': uuid.UUID(response.data['_id'])})
    assert project['description'] == indata['description']
    assert str(project['owners'][0]) == indata['owners'][0]
    assert project['title'] == indata['title']
    assert project['dmp'] == indata['dmp']
    assert project['publications'] == indata['publications']
    assert str(project['datasets'][0]) == indata['datasets'][0]

    as_user(session, USERS['data'])
    
    response = make_request(session,
                            f'/api/project/',
                            method='POST',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    assert '_id' in response.data
    assert len(response.data['_id']) == 36
    project = db['projects'].find_one({'_id': uuid.UUID(response.data['_id'])})
    assert project['description'] == indata['description']
    assert str(project['owners'][0]) == indata['owners'][0]
    assert project['title'] == indata['title']
    assert project['dmp'] == indata['dmp']
    assert project['publications'] == indata['publications']
    assert str(project['datasets'][0]) == indata['datasets'][0]


def test_add_project_log(use_db):
    """
    Add a default dataset using / POST.

    Confirm that logs are created.
    """
    db = use_db

    indata = {'description': 'Test description',
              'receiver': 'new_email@example.com',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/project/',
                                       method='POST',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('projects', 'data', 'root'):
            assert response.code == 200
            assert '_id' in response.data
            assert len(response.data['_id']) == 36
            project = db['projects'].find_one({'_id': uuid.UUID(response.data['_id'])})
            logs = list(db['logs'].find({'data_type': 'project',
                                         'data._id': uuid.UUID(response.data['_id'])}))
            assert len(logs) == 1
            assert logs[0]['data'] == project
            assert logs[0]['action'] == 'add'
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_add_project_bad():
    """
    Add a default dataset using / POST.

    Bad requests.
    """
    indata = {'description': 'Test description',
              'receiver': 'bad_email@asd',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/project/',
                                       method='POST',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('projects', 'data', 'root'):
            assert response.code == 400
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    indata = {'description': 'Test description',
              'creator': 'bad_email@asd',
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/project/',
                                       method='POST',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('projects', 'data', 'root'):
            assert response.code == 400
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    indata = {'description': 'Test description',
              'creator': str(uuid.uuid4()),
              'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/project/',
                                       method='POST',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('data', 'root'):
            assert response.code == 400
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    session = requests.Session()
    as_user(session, USERS['data'])
    indata = {'_id': str(uuid.uuid4()),
              'receiver': 'bad_email@asd',
              'title': 'Test title'}
    indata.update(TEST_LABEL)
    response = make_request(session,
                             f'/api/project/',
                             method='POST',
                             data=indata,
                             ret_json=True)
    assert response.code == 400
    assert not response.data

    indata = {'datasets': [],
              'receiver': 'bad_email@asd',
              'title': 'Test title'}
    indata.update(TEST_LABEL)
    response = make_request(session,
                             f'/api/project/',
                             method='POST',
                             data=indata,
                             ret_json=True)
    assert response.code == 400


def test_list_projects():
    """
    Request a list of all projects.

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles('/api/project/', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['projects']) == 500
