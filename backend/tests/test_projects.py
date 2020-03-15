"""Tests for project requests."""
import json
import uuid
import requests

from helpers import make_request, as_user, make_request_all_roles,\
    USERS, random_string, use_db, TEST_LABEL, project_for_tests, add_dataset, delete_dataset
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

    Confirm:
    * fields are set correctly
    * logs are created
    """
    db = use_db

    dataset_info = next(db['datasets'].aggregate([{'$sample': {'size': 1}}]))
    order_info = db['orders'].find_one({'datasets': dataset_info['_id']})
    session = requests.Session()
    user_info = db['users'].find_one({'_id': order_info['creator']})

    as_user(session, user_info['api_key'])
    
    indata = {'description': 'Test description',
              'contact': 'user@example.com',
              'dmp': 'https://dmp_url_test',
              'owners': [str(user_info['_id'])],
              'publications': [{'title': 'A test publication title',
                                'doi': 'doi://a_test_doi_value'}],
              'title': 'Test title',
              'datasets': [str(dataset_info['_id'])]}
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

    # log
    assert db['logs'].find_one({'data._id': uuid.UUID(response.data['_id']),
                                'data_type': 'project',
                                'user': user_info['_id'],
                                'action': 'add'})
    
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

    data_user = db['users'].find_one({'auth_id': USERS['data']})
    
    # log
    assert db['logs'].find_one({'data._id': uuid.UUID(response.data['_id']),
                                'data_type': 'project',
                                'user': data_user['_id'],
                                'action': 'add'})


def test_add_project_bad():
    """
    Add a default dataset using / POST.

    Bad requests.
    """
    indata = {'title': ''}
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
            assert response.code == 400
            assert not response.data


    indata = {'bad_tag': 'content',
              'title': 'title'}

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
            assert response.code == 400
            assert not response.data

    indata = {'description': 'Test description',
              'owners': [str(uuid.uuid4())],
              'title': 'Test title'}
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
            assert response.code == 400
            assert not response.data

    session = requests.Session()
    as_user(session, USERS['data'])
    indata = {'_id': str(uuid.uuid4()),
              'owners': [str(uuid.uuid4())],
              'title': 'Test title'}
    indata.update(TEST_LABEL)
    response = make_request(session,
                             f'/api/project/',
                             method='POST',
                             data=indata,
                             ret_json=True)
    assert response.code == 403
    assert not response.data

    indata = {'datasets': [str(uuid.uuid4())],
              'title': 'Test title'}
    indata.update(TEST_LABEL)
    response = make_request(session,
                             f'/api/project/',
                             method='POST',
                             data=indata,
                             ret_json=True)
    assert response.code == 400


def test_update_project_permissions(use_db, project_for_tests):
    """
    Update a project.

    Test permissions.
    """
    session = requests.Session()

    db = use_db
    project_uuid = project_for_tests
    print(db['projects'].find_one({'_id': project_uuid}))

    for role in USERS:
        as_user(session, USERS[role])
        indata = {'title': f'Test title - updated by {role}'}
        response = make_request(session,
                                f'/api/project/{project_uuid}/',
                                method='PATCH',
                                data=indata,
                                ret_json=True)
        if role in ('base', 'data', 'root'):
            assert response.code == 200
            assert not response.data
            new_project = db['projects'].find_one({'_id': project_uuid})
            assert new_project['title'] == f'Test title - updated by {role}'
        elif role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_update_project(use_db):
    """
    Update existing projects.

    Confirm that fields are set correctly.
    Confirm that logs are created.
    """
    db = use_db

    uuids = add_dataset()
    project_info = db['projects'].find_one({'_id': uuids[2]})
    user_info = db['users'].find_one({'auth_id': USERS['base']})
    
    indata = {'description': 'Test description updated',
              'contact': 'user_updated@example.com',
              'dmp': 'https://dmp_updated_url_test',
              'owners': [str(project_info['owners'][0])],
              'publications': [{'title': 'Updated publication title',
                                'doi': 'doi://updated_doi_value'}],
              'title': 'Test title updated',
              'datasets': [str(uuids[1])]}
    indata.update(TEST_LABEL)

    session = requests.Session()
    as_user(session, USERS['base'])

    response = make_request(session,
                            f'/api/project/{project_info["_id"]}/',
                            method='PATCH',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    project = db['projects'].find_one({'_id': project_info['_id']})
    assert project['description'] == indata['description']
    assert str(project['owners'][0]) == indata['owners'][0]
    assert project['title'] == indata['title']
    assert project['dmp'] == indata['dmp']
    assert project['publications'] == indata['publications']
    assert str(project['datasets'][0]) == indata['datasets'][0]

    # log
    assert db['logs'].find_one({'data._id': project_info['_id'],
                                'data_type': 'project',
                                'user': user_info['_id'],
                                'action': 'edit'})
    
    as_user(session, USERS['data'])
    user_info = db['users'].find_one({'auth_id': USERS['data']})

    indata = {'description': 'Test description updated2',
              'contact': 'user_updated@example.com2',
              'dmp': 'https://dmp_updated_url_test2',
              'owners': [str(user_info['_id'])],
              'publications': [{'title': 'Updated publication title2',
                                'doi': 'doi://updated_doi_value'}],
              'title': 'Test title updated',
              'datasets': [str(uuids[1]), str(uuids[1])]}
    indata.update(TEST_LABEL)
    
    response = make_request(session,
                            f'/api/project/{project_info["_id"]}/',
                            method='PATCH',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    project = db['projects'].find_one({'_id': project_info['_id']})
    assert project['description'] == indata['description']
    assert str(project['owners'][0]) == indata['owners'][0]
    assert project['title'] == indata['title']
    assert project['dmp'] == indata['dmp']
    assert project['publications'] == indata['publications']
    assert str(project['datasets'][0]) == indata['datasets'][0]

    data_user = db['users'].find_one({'auth_id': USERS['data']})
    
    # log
    assert db['logs'].find_one({'data._id': project_info['_id'],
                                'data_type': 'project',
                                'user': user_info['_id'],
                                'action': 'edit'})
    delete_dataset(*uuids)


def test_update_project_bad(use_db):
    """
    Update an existing project.

    Bad requests.
    """
    db = use_db

    uuids = add_dataset()
    project_info = db['projects'].find_one({'_id': uuids[2]})
    user_info = db['users'].find_one({'auth_id': USERS['base']})
    data_user_info = db['users'].find_one({'auth_id': USERS['base']})

    indata = {'bad_tag': 'value'}

    responses = make_request_all_roles(f'/api/project/{project_info["_id"]}/',
                                       method='PATCH',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('base', 'data', 'root'):
            assert response.code == 400
            assert not response.data
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    indata = {'description': 'Test description',
              'owners': [str(uuid.uuid4())],
              'title': 'Test title'}

    responses = make_request_all_roles(f'/api/project/{project_info["_id"]}/',
                                       method='PATCH',
                                       data=indata,
                                       ret_json=True)
    for response in responses:
        if response.role in ('base', 'data', 'root'):
            assert response.code == 400
            assert not response.data
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    for _ in range(2):
        indata = {'title': 'Test title'}
        responses = make_request_all_roles(f'/api/project/{uuid.uuid4()}/',
                                           method='PATCH',
                                           data=indata,
                                           ret_json=True)
        for response in responses:
            if response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 404
                assert not response.data

        indata = {'title': 'Test title'}
        responses = make_request_all_roles(f'/api/project/{random_string()}/',
                                           method='PATCH',
                                           data=indata,
                                           ret_json=True)
        for response in responses:
            if response.role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 404
                assert not response.data

    delete_dataset(*uuids)


def test_delete_project(use_db):
    """
    Add and delete projects.

    * Check permissions.
    * Delete projects added by the add tests.
    * Confirm that related datasets are deleted.
    * Check that logs are created correctly.
    """
    session = requests.Session()

    db = use_db

    # must be updated if TEST_LABEL is modified
    projects = list(db['projects'].find({'extra.testing': 'yes'}))
    i = 0
    while i < len(projects):
        for role in USERS:
            as_user(session, USERS[role])
            response = make_request(session,
                                    f'/api/project/{projects[i]["_id"]}/',
                                    method='DELETE')
            if role in ('data', 'root'):
                assert response.code == 200
                assert not response.data
                assert not db['projects'].find_one({'_id': projects[i]['_id']})
                assert db['logs'].find_one({'data._id': projects[i]['_id'],
                                            'action': 'delete',
                                            'data_type': 'project'})
                i += 1
                if i >= len(projects):
                    break
            elif role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                current_user = db['users'].find_one({'auth_id': USERS[role]})
                if current_user['_id'] in projects[i]['owners']:
                    assert response.code == 200
                    assert not response.data
                    assert not db['projects'].find_one({'_id': projects[i]['_id']})
                    assert db['logs'].find_one({'data._id': projects[i]['_id'],
                                                'action': 'delete',
                                                'data_type': 'project'})
                    i += 1
                    if i >= len(projects):
                        break

                else:
                    assert response.code == 403
                    assert not response.data

    as_user(session, USERS['base'])
    response = make_request(session,
                            f'/api/project/',
                            data={'title': 'tmp'},
                            method='POST')
    assert response.code == 200
    response = make_request(session,
                            f'/api/project/{response.data["_id"]}/',
                            method='DELETE')
    assert response.code == 200
    assert not response.data


def test_delete_project_bad():
    """Attempt bad project delete requests."""
    session = requests.Session()

    as_user(session, USERS['data'])
    for _ in range(2):
        response = make_request(session,
                                f'/api/project/{random_string()}/',
                                method='DELETE')
    assert response.code == 404
    assert not response.data

    for _ in range(2):
        response = make_request(session,
                                f'/api/project/{uuid.uuid4()}/',
                                method='DELETE')
    assert response.code == 404
    assert not response.data


def test_list_projects():
    """
    Request a list of all projects.

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles('/api/project/', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['projects']) == 500
