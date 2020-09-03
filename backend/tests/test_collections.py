"""Tests for collection requests."""
import json
import uuid
import requests

from helpers import make_request, as_user, make_request_all_roles,\
    USERS, random_string, use_db, TEST_LABEL, collection_for_tests, add_dataset, delete_dataset
# pylint: disable=redefined-outer-name

def test_random_collection():
    """Request a random collection."""
    responses = make_request_all_roles('/api/collection/random', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['collections']) == 1


def test_random_collections():
    """Request random collections."""
    session = requests.Session()
    as_user(session, USERS['base'])
    for i in (1, 5, 0):
        response = make_request(session, f'/api/collection/random/{i}', ret_json=True)
        assert response.code == 200
        assert len(response.data['collections']) == i

    response = make_request(session, '/api/collection/random/-1')
    assert response[1] == 404
    assert not response[0]


def test_get_collection_permissions(use_db):
    """Test permissions for requesting a collection."""
    db = use_db
    collection = list(db['collections'].aggregate([{'$sample': {'size': 1}}]))[0]

    responses = make_request_all_roles(f'/api/collection/{collection["_id"]}', ret_json=True)
    for response in responses:
        assert response.code == 200


def test_get_collection(use_db):
    """
    Request multiple collections by uuid, one at a time.

    Collections are choosen randomly using /api/collection/random.
    """
    db = use_db
    session = requests.Session()
    for _ in range(3):
        collection = list(db['collections'].aggregate([{'$sample': {'size': 1}}]))[0]
        owner_emails = [db['users'].find_one({'$or': [{'_id': identifier},
                                                      {'email': identifier}]})['email']
                        for identifier in collection['owners']]
        collection['_id'] = str(collection['_id'])
        proj_owner = db['users'].find_one({'_id': collection['owners'][0]})
        if not proj_owner:
            proj_owner = db['users'].find_one({'email': collection['owners'][0]})
        if not proj_owner:
            print('Unknown user for owner')
            assert False
        collection['owners'] = [str(entry) for entry in collection['owners']]

        collection['datasets'] = [str(entry) for entry in collection['datasets']]
        response = make_request(session, f'/api/collection/{collection["_id"]}')
        assert response.code == 200
        for field in collection:
            if field == 'datasets':
                for i, ds_uuid in enumerate(collection[field]):
                    assert ds_uuid == response.data['collection'][field][i]['_id']
            elif field != 'owners':
                assert collection[field] == response.data['collection'][field]
            else:
                if field in response.data['collection']:
                    assert response.data['collection'][field] == owner_emails
        as_user(session, proj_owner['auth_id'])
        response = make_request(session, f'/api/collection/{collection["_id"]}')
        assert response.code == 200
        for field in collection:
            if field == 'datasets':
                for i, ds_uuid in enumerate(collection[field]):
                    assert ds_uuid == response.data['collection'][field][i]['_id']
            elif field == 'owners':
                assert response.data['collection'][field] == owner_emails
            else:
                assert collection[field] == response.data['collection'][field]
        as_user(session, USERS['root'])
        response = make_request(session, f'/api/collection/{collection["_id"]}')
        assert response.code == 200
        for field in collection:
            if field == 'datasets':
                for i, ds_uuid in enumerate(collection[field]):
                    assert ds_uuid == response.data['collection'][field][i]['_id']
            elif field == 'owners':
                assert response.data['collection'][field] == owner_emails
            else:
                assert collection[field] == response.data['collection'][field]


def test_get_collection_bad():
    """
    Request collections using bad identifiers.

    All are expected to return 404.
    """
    session = requests.Session()
    for _ in range(2):
        response = make_request(session, f'/api/collection/{uuid.uuid4().hex}')
        assert response.code == 404
        assert not response.data

    for _ in range(2):
        response = make_request(session, f'/api/collection/{random_string()}')
        assert response.code == 404
        assert not response.data


def test_add_collection_permissions(use_db):
    """
    Add a collection.

    Test permissions.
    """
    db = use_db
    
    indata = {'title': 'Test title'}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/collection/',
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

    responses = make_request_all_roles(f'/api/collection/',
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

    dataset_info = next(db['datasets'].aggregate([{'$sample': {'size': 1}}]))
    order_info = db['orders'].find_one({'datasets': dataset_info['_id']})
    user_info = db['users'].find_one({'_id': order_info['creator']})
    indata.update({'owners': [str(user_info['_id'])],
                   'datasets': [str(dataset_info['_id'])]})

    session = requests.Session()
    as_user(session, user_info['auth_id'])
    response = make_request(session,
                            f'/api/collection/',
                            method='POST',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    assert '_id' in response.data
    assert len(response.data['_id']) == 36
    
    responses = make_request_all_roles(f'/api/collection/',
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
    
    
def test_add_collection(use_db):
    """
    Add a collection.

    Confirm:
    * fields are set correctly
    * logs are created
    """
    db = use_db

    dataset_info = next(db['datasets'].aggregate([{'$sample': {'size': 1}}]))
    order_info = db['orders'].find_one({'datasets': dataset_info['_id']})
    session = requests.Session()
    user_info = db['users'].find_one({'_id': order_info['creator']})

    as_user(session, user_info['auth_id'])
    
    indata = {'description': 'Test description',
              'contact': 'user@example.com',
              'dmp': 'https://dmp_url_test',
              'owners': [str(user_info['_id'])],
              'publications': ['A test publication title, doi://a_test_doi_value'],
              'title': 'Test title',
              'datasets': [str(dataset_info['_id'])]}
    indata.update(TEST_LABEL)

    response = make_request(session,
                            f'/api/collection/',
                            method='POST',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    assert '_id' in response.data
    assert len(response.data['_id']) == 36
    collection = db['collections'].find_one({'_id': uuid.UUID(response.data['_id'])})
    assert collection['description'] == indata['description']
    assert str(collection['owners'][0]) == indata['owners'][0]
    assert collection['title'] == indata['title']
    assert collection['dmp'] == indata['dmp']
    assert collection['publications'] == indata['publications']
    assert str(collection['datasets'][0]) == indata['datasets'][0]

    # log
    assert db['logs'].find_one({'data._id': uuid.UUID(response.data['_id']),
                                'data_type': 'collection',
                                'user': user_info['_id'],
                                'action': 'add'})
    
    as_user(session, USERS['data'])
    
    response = make_request(session,
                            f'/api/collection/',
                            method='POST',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    assert '_id' in response.data
    assert len(response.data['_id']) == 36
    collection = db['collections'].find_one({'_id': uuid.UUID(response.data['_id'])})
    assert collection['description'] == indata['description']
    assert str(collection['owners'][0]) == indata['owners'][0]
    assert collection['title'] == indata['title']
    assert collection['dmp'] == indata['dmp']
    assert collection['publications'] == indata['publications']
    assert str(collection['datasets'][0]) == indata['datasets'][0]

    data_user = db['users'].find_one({'auth_id': USERS['data']})
    
    # log
    assert db['logs'].find_one({'data._id': uuid.UUID(response.data['_id']),
                                'data_type': 'collection',
                                'user': data_user['_id'],
                                'action': 'add'})


def test_add_collection_bad():
    """
    Add a default dataset using / POST.

    Bad requests.
    """
    indata = {'title': ''}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/collection/',
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


    indata = {}
    indata.update(TEST_LABEL)

    responses = make_request_all_roles(f'/api/collection/',
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

    responses = make_request_all_roles(f'/api/collection/',
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

    responses = make_request_all_roles(f'/api/collection/',
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
                             f'/api/collection/',
                             method='POST',
                             data=indata,
                             ret_json=True)
    assert response.code == 403
    assert not response.data

    indata = {'datasets': [str(uuid.uuid4())],
              'title': 'Test title'}
    indata.update(TEST_LABEL)
    response = make_request(session,
                             f'/api/collection/',
                             method='POST',
                             data=indata,
                             ret_json=True)
    assert response.code == 400


def test_update_collection_permissions(use_db, collection_for_tests):
    """
    Update a collection.

    Test permissions.
    """
    session = requests.Session()

    db = use_db
    collection_uuid = collection_for_tests
    print(db['collections'].find_one({'_id': collection_uuid}))

    for role in USERS:
        as_user(session, USERS[role])
        indata = {'title': f'Test title - updated by {role}'}
        response = make_request(session,
                                f'/api/collection/{collection_uuid}/',
                                method='PATCH',
                                data=indata,
                                ret_json=True)
        if role in ('base', 'data', 'root'):
            assert response.code == 200
            assert not response.data
            new_collection = db['collections'].find_one({'_id': collection_uuid})
            assert new_collection['title'] == f'Test title - updated by {role}'
        elif role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_update_collection(use_db):
    """
    Update existing collections.

    Confirm that fields are set correctly.
    Confirm that logs are created.
    """
    db = use_db

    uuids = add_dataset()
    collection_info = db['collections'].find_one({'_id': uuids[2]})
    user_info = db['users'].find_one({'auth_id': USERS['base']})
    
    indata = {'description': 'Test description updated',
              'contact': 'user_updated@example.com',
              'dmp': 'https://dmp_updated_url_test',
              'owners': [str(collection_info['owners'][0])],
              'publications': ['Updated publication title, doi://updated_doi_value'],
              'title': 'Test title updated',
              'datasets': [str(uuids[1])]}
    indata.update(TEST_LABEL)

    session = requests.Session()
    as_user(session, USERS['base'])

    response = make_request(session,
                            f'/api/collection/{collection_info["_id"]}/',
                            method='PATCH',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    collection = db['collections'].find_one({'_id': collection_info['_id']})
    assert collection['description'] == indata['description']
    assert str(collection['owners'][0]) == indata['owners'][0]
    assert collection['title'] == indata['title']
    assert collection['dmp'] == indata['dmp']
    assert collection['publications'] == indata['publications']
    assert str(collection['datasets'][0]) == indata['datasets'][0]

    # log
    assert db['logs'].find_one({'data._id': collection_info['_id'],
                                'data_type': 'collection',
                                'user': user_info['_id'],
                                'action': 'edit'})
    
    as_user(session, USERS['data'])
    user_info = db['users'].find_one({'auth_id': USERS['data']})

    indata = {'description': 'Test description updated2',
              'contact': 'user_updated@example.com2',
              'dmp': 'https://dmp_updated_url_test2',
              'owners': [str(user_info['_id'])],
              'publications': ['Updated publication title2, doi://updated_doi_value'],
              'title': 'Test title updated',
              'datasets': [str(uuids[1]), str(uuids[1])]}
    indata.update(TEST_LABEL)
    
    response = make_request(session,
                            f'/api/collection/{collection_info["_id"]}/',
                            method='PATCH',
                            data=indata,
                            ret_json=True)
    assert response.code == 200
    collection = db['collections'].find_one({'_id': collection_info['_id']})
    assert collection['description'] == indata['description']
    assert str(collection['owners'][0]) == indata['owners'][0]
    assert collection['title'] == indata['title']
    assert collection['dmp'] == indata['dmp']
    assert collection['publications'] == indata['publications']
    assert str(collection['datasets'][0]) == indata['datasets'][0]

    data_user = db['users'].find_one({'auth_id': USERS['data']})
    
    # log
    assert db['logs'].find_one({'data._id': collection_info['_id'],
                                'data_type': 'collection',
                                'user': user_info['_id'],
                                'action': 'edit'})
    delete_dataset(*uuids)


def test_update_collection_bad(use_db):
    """
    Update an existing collection.

    Bad requests.
    """
    db = use_db

    uuids = add_dataset()
    collection_info = db['collections'].find_one({'_id': uuids[2]})
    user_info = db['users'].find_one({'auth_id': USERS['base']})
    data_user_info = db['users'].find_one({'auth_id': USERS['base']})

    indata = {'bad_tag': 'value'}

    responses = make_request_all_roles(f'/api/collection/{collection_info["_id"]}/',
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

    responses = make_request_all_roles(f'/api/collection/{collection_info["_id"]}/',
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
        responses = make_request_all_roles(f'/api/collection/{uuid.uuid4()}/',
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
        responses = make_request_all_roles(f'/api/collection/{random_string()}/',
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


def test_delete_collection(use_db):
    """
    Add and delete collections.

    * Check permissions.
    * Delete collections added by the add tests.
    * Confirm that related datasets are deleted.
    * Check that logs are created correctly.
    """
    session = requests.Session()

    db = use_db

    # must be updated if TEST_LABEL is modified
    collections = list(db['collections'].find({'extra.testing': 'yes'}))
    i = 0
    while i < len(collections):
        for role in USERS:
            as_user(session, USERS[role])
            response = make_request(session,
                                    f'/api/collection/{collections[i]["_id"]}/',
                                    method='DELETE')
            if role in ('data', 'root'):
                assert response.code == 200
                assert not response.data
                assert not db['collections'].find_one({'_id': collections[i]['_id']})
                assert db['logs'].find_one({'data._id': collections[i]['_id'],
                                            'action': 'delete',
                                            'data_type': 'collection'})
                i += 1
                if i >= len(collections):
                    break
            elif role == 'no-login':
                assert response.code == 401
                assert not response.data
            else:
                current_user = db['users'].find_one({'auth_id': USERS[role]})
                if current_user['_id'] in collections[i]['owners']:
                    assert response.code == 200
                    assert not response.data
                    assert not db['collections'].find_one({'_id': collections[i]['_id']})
                    assert db['logs'].find_one({'data._id': collections[i]['_id'],
                                                'action': 'delete',
                                                'data_type': 'collection'})
                    i += 1
                    if i >= len(collections):
                        break

                else:
                    assert response.code == 403
                    assert not response.data

    as_user(session, USERS['base'])
    response = make_request(session,
                            f'/api/collection/',
                            data={'title': 'tmp'},
                            method='POST')
    assert response.code == 200
    response = make_request(session,
                            f'/api/collection/{response.data["_id"]}/',
                            method='DELETE')
    assert response.code == 200
    assert not response.data


def test_delete_collection_bad():
    """Attempt bad collection delete requests."""
    session = requests.Session()

    as_user(session, USERS['data'])
    for _ in range(2):
        response = make_request(session,
                                f'/api/collection/{random_string()}/',
                                method='DELETE')
    assert response.code == 404
    assert not response.data

    for _ in range(2):
        response = make_request(session,
                                f'/api/collection/{uuid.uuid4()}/',
                                method='DELETE')
    assert response.code == 404
    assert not response.data


def test_list_collections():
    """
    Request a list of all collections.

    Should also test e.g. pagination once implemented.
    """
    responses = make_request_all_roles('/api/collection/', ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data['collections']) == 500


def test_get_collection_logs_permissions(use_db):
    """
    Get collection logs.

    Assert that DATA_MANAGEMENT or user in owners is required.
    """
    db = use_db
    collection_data = db['collections'].aggregate([{'$sample': {'size': 1}}]).next()
    user_data = db['users'].find_one({'$or': [{'_id': collection_data['owners'][0]},
                                              {'email': collection_data['owners'][0]}]})
    responses = make_request_all_roles(f'/api/collection/{collection_data["_id"]}/log/',
                                       ret_json=True)
    for response in responses:
        if response.role in ('data', 'root'):
            assert response.code == 200
            assert 'logs' in response.data
        elif response.role == 'no-login':
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    session = requests.Session()

    as_user(session, user_data['auth_id'])
    response = make_request(session,
                             f'/api/collection/{collection_data["_id"]}/log/',
                             ret_json=True)

    assert response.code == 200
    assert 'logs' in response.data


def test_get_collection_logs(use_db):
    """
    Request the logs for multiple collections.

    Confirm that the logs contain only the intended fields.
    """
    session = requests.session()
    db = use_db
    collections = db['collections'].aggregate([{'$sample': {'size': 2}}])
    for collection in collections:
        logs = list(db['logs'].find({'data_type': 'collection', 'data._id': collection['_id']}))
        as_user(session, USERS['data'])
        response = make_request(session, f'/api/collection/{collection["_id"]}/log/', ret_json=True)
        assert response.data['dataType'] == 'collection'
        assert response.data['entryId'] == str(collection['_id'])
        assert len(response.data['logs']) == len(logs)
        assert response.code == 200
