"""Tests for the handlers in application.py."""

import json
import os
import requests

import pytest

curr_dir = os.path.realpath(__file__)
settings = json.loads(open(f'{os.path.dirname(curr_dir)}/settings_tests.json').read())
BASE_URL = f'{settings["host"]}:{settings["port"]}'

@pytest.fixture
def dataset_for_tests():
    # prepare
    session = requests.Session()
    as_user(session, 5)
    payload = {'dataset': {'title': 'A Unique Title',
                           'description': 'Description',
                           'doi': 'DOI',
                           'creator': 'Creator',
                           'contact': 'Contact',
                           'dmp': 'Data Management Plan',
                           'visible': True,
                           'tags': [{'title': 'Tag1'}, {'title': 'Tag2'}],
                           'publications': [{'identifier': 'Publication'}],
                           'dataUrls': [{'url': 'Data Access URL', 'description': 'Description'}],
                           'owners': [{'email': 'user3@example.com'}]}}

    _, status_code = make_request(session,
                                  '/api/dataset/add',
                                  payload)

    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     {'query': {'title': 'A Unique Title'}})
    ds_id = data['datasets'][0]['id']

    yield ds_id

    # cleanup
    payload = {'identifier': ds_id}
    _, status_code = make_request(session,
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
        session.headers['X-Xsrftoken'] = session.cookies['_xsrf']
    else:
        code = session.get(f'{BASE_URL}/logout').status_code
        session.get(f'{BASE_URL}/api/datasets')  # reset cookies
        session.headers['X-Xsrftoken'] = session.cookies['_xsrf']
    return code


def test_add_dataset_get():
    """Test AddDataset.get()"""
    session = requests.Session()
    expected = {'dataset': {'title': 'Title',
                            'description': 'Description',
                            'doi': 'DOI',
                            'creator': 'Creator',
                            'contact': 'Contact',
                            'dmp': 'Data Management Plan',
                            'visible': True,
                            'tags': [{'title': 'Tag1'}, {'title': 'Tag2'}],
                            'publications': [{'identifier': 'Publication'}],
                            'dataUrls': [{'url': 'Data Access URL', 'description': 'Description'}],
                            'owners': [{'email': 'Owner email'}]}}

    # not logged in
    as_user(session, 0)
    data, status_code = make_request(session, '/api/dataset/add')
    assert status_code == 403
    assert not data

    # normal user
    as_user(session, 1)
    data, status_code = make_request(session, '/api/dataset/add')
    assert status_code == 403
    assert not data

    # steward
    as_user(session, 5)
    data, status_code = make_request(session, '/api/dataset/add')
    assert status_code == 200
    assert data == expected

    # admin
    as_user(session, 5)
    data, status_code = make_request(session, '/api/dataset/add')
    assert status_code == 200
    assert data == expected


def test_add_dataset_post():
    """Test AddDataset.post()"""
    session = requests.Session()
    payload = {'dataset': {'title': 'An added Dataset1',
                           'description': 'Description of added dataset1',
                           'doi': 'A doi for added dataset1',
                           'creator': 'The facility that created dataset1',
                           'contact': 'Contact for added dataset1',
                           'dmp': 'Url to dmp for added dataset1',
                           'tags': [{'title': 'Tag Title 7'},
                                    {'title': 'Tag Title 1'},
                                    {'title': 'Tag Title 5'}],
                           'publications': [{'identifier': 'Publication title1. Journal:Year'}],
                           'dataUrls': [{'description': 'Part I', 'url': 'Data url 1a'},
                                        {'description': 'Part II', 'url': 'Data url 1b'}],
                           'owners': [{'email': 'user1@example.com'}],
                           'visible': True}}

    # steward
    as_user(session, 5)
    data, status_code = make_request(session,
                                     '/api/dataset/add',
                                     payload)
    assert status_code == 200
    assert not data

    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     {'query': {'title': payload['dataset']['title']}})
    assert status_code == 200
    dbid = data['datasets'][0]['id']
    data, status_code = make_request(session, f'/api/dataset/{dbid}')
    assert status_code == 200
    for header in payload['dataset']:
        if header == 'owners':
            assert sorted([owner['name'] for owner in data[header]]) == ['A Name1']
        else:
            if header == 'publications':
                assert (sorted([pub['identifier'] for pub in data[header]]) ==
                        sorted([pub['identifier'] for pub in payload['dataset'][header]]))
            elif header == 'tags':
                assert (sorted([tag['title'] for tag in data[header]]) ==
                        sorted([tag['title'] for tag in payload['dataset'][header]]))
            elif header == 'dataUrls':
                assert (sorted([url['url'] for url in data['dataUrls']]) ==
                        sorted([url['url'] for url in payload['dataset'][header]]))
                assert (sorted([url['description'] for url in data['dataUrls']]) ==
                        sorted([url['description'] for url in payload['dataset'][header]]))
            else:
                assert data[header] == payload['dataset'][header]

    ## bad requests
    data, status_code = make_request(session,
                                     '/api/dataset/add',
                                     {'bad_request': None})
    assert status_code == 400
    assert not data
    data, status_code = make_request(session,
                                     '/api/dataset/add',
                                     {'dataset': {'title_missing': None}})
    assert status_code == 400
    assert not data
    data, status_code = make_request(session,
                                     '/api/dataset/add',
                                     {'dataset': {'title': ''}})
    assert status_code == 400
    assert not data

    # admin
    as_user(session, 6)
    payload['dataset']['title'] = 'An added Dataset2'
    payload['dataset']['owners'].append({'email': 'user2@example.com'})

    data, status_code = make_request(session,
                                     '/api/dataset/add',
                                     payload)
    assert status_code == 200
    assert not data

    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     {'query': {'title': payload['dataset']['title']}})
    assert status_code == 200
    dbid = data['datasets'][0]['id']
    data, status_code = make_request(session,
                                     f'/api/dataset/{dbid}')
    assert status_code == 200
    for header in payload['dataset']:
        if header == 'owners':
            assert sorted([owner['name'] for owner in data[header]]) == ['A Name1', 'A Name2']
        else:
            if header == 'publications':
                assert (sorted([pub['identifier'] for pub in data[header]]) ==
                        sorted([pub['identifier'] for pub in payload['dataset'][header]]))
            elif header == 'tags':
                assert (sorted([tag['title'] for tag in data[header]]) ==
                        sorted([tag['title'] for tag in payload['dataset'][header]]))
            elif header == 'dataUrls':
                assert (sorted([url['url'] for url in data['dataUrls']]) ==
                        sorted([url['url'] for url in payload['dataset'][header]]))
                assert (sorted([url['description'] for url in data['dataUrls']]) ==
                        sorted([url['description'] for url in payload['dataset'][header]]))
            else:
                assert data[header] == payload['dataset'][header]

    # not logged in: fail
    as_user(session, 0)
    data, status_code = make_request(session,
                                     f'/api/dataset/add',
                                     payload)
    assert status_code == 403
    assert not data

    # normal user: fail
    as_user(session, 1)
    data, status_code = make_request(session,
                                     f'/api/dataset/add',
                                     payload)
    assert status_code == 403
    assert not data


def test_countrylist_get():
    """Test CountryList.get()"""
    response = requests.get(f'{BASE_URL}/api/countries')
    assert response.status_code == 200
    data = json.loads(response.text)

    assert len(data['countries']) == 240


def test_delete_dataset_get(dataset_for_tests):
    """Test DeleteDataset.get()"""
    session = requests.Session()
    expected = {'identifier': 9876543210}

    # not logged in/normal user
    for user in (0, 1):
        as_user(session, user)
        data, status_code = make_request(session, '/api/dataset/delete')
        assert status_code == 403
        assert not data
        data, status_code = make_request(session, '/api/dataset/4/delete')
        assert status_code == 403
        assert not data
    # steward
    as_user(session, 5)
    data, status_code = make_request(session, '/api/dataset/delete')
    assert status_code == 200
    assert data == expected
    data, status_code = make_request(session, f'/api/dataset/{dataset_for_tests}/delete')
    assert status_code == 200
    assert not data
    # admin
    as_user(session, 6)
    data, status_code = make_request(session, '/api/dataset/delete')
    assert status_code == 200
    assert data == expected


def test_delete_dataset_post():
    """Test DeleteDataset.post()"""
    session = requests.Session()
    # steward
    ## will delete the dataset added as steward in test_add_dataset_post()
    as_user(session, 5)
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     {'query': {'title': 'An added Dataset1'}})
    assert status_code == 200
    dbid = data['datasets'][0]['id']
    payload = {'identifier': dbid}
    data, status_code = make_request(session,
                                     '/api/dataset/delete',
                                     payload)
    assert status_code == 200
    assert not data

    ## bad requests
    for payload in ({'identifier': 'abc'},
                    {'identifier': 10**7}):
        data, status_code = make_request(session,
                                         '/api/dataset/delete',
                                         payload)
    assert status_code == 400
    assert not data

    # admin
    ## will delete the dataset added as admin in test_add_dataset_post()
    as_user(session, 6)
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     {'query': {'title': 'An added Dataset2'}})
    assert status_code == 200
    dbid = data['datasets'][0]['id']
    payload = {'identifier': dbid}
    data, status_code = make_request(session,
                                     '/api/dataset/delete',
                                     payload)
    assert status_code == 200
    assert not data

    # not logged in: fail
    as_user(session, 0)
    data, status_code = make_request(session,
                                     '/api/dataset/delete',
                                     payload)
    assert status_code == 403
    assert not data

    # normal user: fail
    as_user(session, 1)
    data, status_code = make_request(session,
                                     '/api/dataset/delete',
                                     payload)
    assert status_code == 403
    assert not data


def test_find_dataset_get():
    """Test DeleteDataset.get()"""
    session = requests.Session()
    expected = {'query': {'title': 'Title',
                          'creator': 'Creator',
                          'tags': ['Tag1'],
                          'publications': ['Title. Journal:Year'],
                          'owners': ['Name1']}}

    for user in (0, 1, 5, 6):
        as_user(session, user)
        data, status_code = make_request(session,
                                         '/api/dataset/query')
        assert status_code == 200
        assert data == expected


def test_find_dataset_post():
    """Test FindDataset.post()"""
    session = requests.Session()
    # not logged in
    as_user(session, 0)
    payload = {'query': {'title': 'Dataset title 2'}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 1

    payload = {'query': {'title': 'Dataset title'}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 4
    for dataset in data['datasets']:
        assert len(dataset) == 8

    payload = {'query': {'title': 'Dataset title',
                         'owners': ['A Name4']}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 2
    for dataset in data['datasets']:
        assert payload['query']['title'] in dataset['title']
        data, status_code = make_request(session,
                                         f'/api/dataset/{dataset["id"]}')
        assert status_code == 200
        for owner in payload['query']['owners']:
            assert owner in [val['name'] for val in data['owners']]

    payload = {'query': {'title': 'Dataset title',
                         'owner': ['A Name1'],
                         'publications': ['A publication1. Journal:2011']}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 1
    for dataset in data['datasets']:
        assert payload['query']['title'] in dataset['title']
        response = session.get(f'{BASE_URL}/api/dataset/{dataset["id"]}')
        data = json.loads(response.text)
        for pub in payload['query']['publications']:
            assert pub in [val['identifier'] for val in data['publications']]

    payload = {'query': {'tags': ['Tag Title 7']}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 1
    for dataset in data['datasets']:
        response = session.get(f'{BASE_URL}/api/dataset/{dataset["id"]}')
        data = json.loads(response.text)
        for tag in payload['query']['tags']:
            assert tag in [val['title'] for val in data['tags']]

    ## bad queries
    for payload in ({'query': {}},
                    {'query': {'bad_type': None}}):
        data, status_code = make_request(session,
                                         '/api/dataset/query',
                                         payload)
        assert status_code == 400
        assert not data

    # normal user
    as_user(session, 1)
    payload = {'query': {'title': 'Dataset title'}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 4

    payload = {'query': {'title': 'Dataset title',
                         'owners': ['A Name4']}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 2
    for dataset in data['datasets']:
        assert payload['query']['title'] in dataset['title']
        response = session.get(f'{BASE_URL}/api/dataset/{dataset["id"]}')
        data = json.loads(response.text)
        for owner in payload['query']['owners']:
            assert owner in [val['name'] for val in data['owners']]

    # owner
    as_user(session, 4)
    payload = {'query': {'title': 'Dataset title'}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 5

    payload = {'query': {'tags': ['Tag Title 7']}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 2
    for dataset in data['datasets']:
        response = session.get(f'{BASE_URL}/api/dataset/{dataset["id"]}')
        data = json.loads(response.text)
        for tag in payload['query']['tags']:
            assert tag in [val['title'] for val in data['tags']]

    # steward
    as_user(session, 5)
    payload = {'query': {'title': 'Dataset title'}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 6

    payload = {'query': {'title': 'Dataset title',
                         'owners': ['A Name4']}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 3

    # admin
    as_user(session, 6)
    payload = {'query': {'title': 'Dataset title'}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 6

    payload = {'query': {'title': 'Dataset title',
                         'owners': ['A Name4']}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 3


def test_get_dataset_get():
    """Test GetDataset.get()"""
    session = requests.Session()
    # not logged in
    data, status_code = make_request(session, '/api/dataset/1')
    assert status_code == 200
    assert len(data) == 11
    assert len(data['tags']) == 5

    tag_titles = [tag['title'] for tag in data['tags']]
    for i in [2, 3, 4, 5, 8]:
        assert f'Tag Title {i}' in tag_titles

    data_urls = [data_url['url'] for data_url in data['dataUrls']]
    for i in [1, 2]:
        assert f'https:www.example.com/url{i}' in data_urls

    data, status_code = make_request(session, '/api/dataset/3')
    assert status_code == 200
    assert not data['tags']
    assert len(data['publications']) == 1
    assert data['publications'][0]['identifier'] == 'A publication2. Journal:2012'

    data, status_code = make_request(session, '/api/dataset/2')
    assert status_code == 200
    assert not data['dataUrls']
    assert not data['publications']


    # owned by user
    as_user(session, 4)
    data, status_code = make_request(session, '/api/dataset/4')
    assert status_code == 200
    assert len(data) == 11

    # steward
    as_user(session, 5)
    data, status_code = make_request(session, '/api/dataset/4')
    assert status_code == 200
    assert len(data) == 11

    # admin
    as_user(session, 6)
    data, status_code = make_request(session, '/api/dataset/4')
    assert status_code == 200
    assert len(data) == 11

    # forbidden
    for user in (0, 1):
        as_user(session, user)
        data, status_code = make_request(session, '/api/dataset/4')
        assert status_code == 403
        assert not data

    # not found
    data, status_code = make_request(session, '/api/dataset/1234567')
    assert status_code == 404
    assert not data


def test_get_user_get():
    """Test GetUser.get()"""
    session = requests.Session()
    # not logged in
    as_user(session, 0)
    data, status_code = make_request(session, '/api/users/me')
    assert status_code == 200
    assert data == {"user": None,
                    "email": None}

    # logged in user
    as_user(session, 4)
    data, status_code = make_request(session, '/api/users/me')
    assert status_code == 200
    assert data == {"user": "A Name4",
                    "email": "user4@example.com",
                    "affiliation": "A University4",
                    "country": "A Country4"}


def test_list_datasets_get():
    """Test ListDatasets.get()"""
    session = requests.Session()
    as_user(session, 0)
    data, status_code = make_request(session, '/api/datasets')
    assert status_code == 200
    assert len(data['datasets']) == 4
    assert data['datasets'][0]['title'] == f"Dataset title {data['datasets'][0]['id']}"

    # log in as user, no extra
    as_user(session, 1)
    data, status_code = make_request(session, '/api/datasets')
    assert status_code == 200
    assert len(data['datasets']) == 4

    # log in as user that owns dataset and list extra
    as_user(session, 4)
    data, status_code = make_request(session, '/api/datasets')
    assert status_code == 200
    assert len(data['datasets']) == 5
    assert {"id": 4, "title": "Dataset title 4"} in data['datasets']

    # log in as steward and list extra
    as_user(session, 5)
    data, status_code = make_request(session, '/api/datasets')
    assert status_code == 200
    assert len(data['datasets']) == 6
    assert {"id": 4, "title": "Dataset title 4"} in data['datasets']

    # log in as admin and list extra
    as_user(session, 6)
    data, status_code = make_request(session, '/api/datasets')
    assert status_code == 200
    assert len(data['datasets']) == 6
    assert {"id": 4, "title": "Dataset title 4"} in data['datasets']


def test_list_user_get():
    """Test ListUser.get()"""
    session = requests.Session()
    for user in (0, 1, 5):
        as_user(session, user)
        data, status_code = make_request(session, '/api/users')
        assert status_code == 403
        assert not data

    # Admin user - list users
    as_user(session, 6)
    data, status_code = make_request(session, '/api/users')
    assert status_code == 200
    assert len(data['users']) == 6
    assert {"id": 5,
            "name": "A Name5",
            "email": "user5@example.com",
            "authIdentity": "user5auth",
            "affiliation": "A University5",
            "country": "A Country5",
            "permission": "Steward"} in data['users']


def test_update_dataset_get():
    """Test UpdateDataset.get()"""
    session = requests.Session()
    expected = {'dataset': {'title': 'Title',
                            'description': 'Description',
                            'doi': 'DOI',
                            'creator': 'Creator',
                            'contact': 'Contact',
                            'dmp': 'Data Management Plan',
                            'visible': True,
                            'tags': [{'title': 'Tag1'}, {'title': 'Tag2'}],
                            'publications': [{'identifier': 'Publication'}],
                            'dataUrls': [{'url': 'Data Access URL', 'description': 'Description'}],
                            'owners': [{'email': 'Owner email'}]}}

    for user in (0, 1):
        as_user(session, user)
        data, status_code = make_request(session, '/api/dataset/4/update')
        assert status_code == 403
        assert not data

    for user in (4, 5, 6):
        as_user(session, user)
        data, status_code = make_request(session, '/api/dataset/4/update')
        assert status_code == 200
        assert data == expected


def test_update_dataset_post(dataset_for_tests):
    """Test UpdateDataset.post()"""
    ds_id = dataset_for_tests
    session = requests.Session()

    # not logged in, normal user
    for user in (0, 1):
        as_user(session, user)
        update_payload = {'dataset': {'title': 'New title'}}
        data, status_code = make_request(session,
                                         f'/api/dataset/{ds_id}/update',
                                         update_payload)
        assert status_code == 403
        assert not data

    # owner
    as_user(session, 3)

    update_payload = {'dataset': {'title': 'New title'}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 200
    assert not data
    data, status_code = make_request(session, f'/api/dataset/{ds_id}')
    assert status_code == 200
    assert data['title'] == 'New title'

    update_payload = {'dataset': {'contact': 'New contact'}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 200
    assert not data
    data, status_code = make_request(session, f'/api/dataset/{ds_id}')
    assert status_code == 200
    assert data['contact'] == 'New contact'

    update_payload = {'dataset': {'contact': 'New contact2',
                                  'tags': [{'title': 'Tag1'},
                                           {'title': 'NewTag1'},
                                           {'title': 'NewTag2'}]}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 200
    assert not data
    data, status_code = make_request(session, f'/api/dataset/{ds_id}')
    assert status_code == 200
    assert data['contact'] == 'New contact2'
    tags = [tag['title'] for tag in data['tags']]
    assert len(tags) == 3
    for tag in ('Tag1', 'NewTag1', 'NewTag2'):
        assert tag in tags

    update_payload = {'dataset': {'doi': 'new doi',
                                  'dataUrls': [{'description': 'Some kinda data1',
                                                'url': 'http://example.com/1'},
                                               {'description': 'Some kinda data2',
                                                'url': 'http://example.com/2'}]}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 200
    assert not data
    data, status_code = make_request(session, f'/api/dataset/{ds_id}')
    assert status_code == 200
    assert data['doi'] == 'new doi'
    data_descs = [url['description'] for url in data['dataUrls']]
    data_urls = [url['url'] for url in data['dataUrls']]
    assert len(data_descs) == 2
    assert len(data_urls) == 2
    for data_desc in ('Some kinda data1', 'Some kinda data2'):
        assert data_desc in data_descs
    for data_url in ('http://example.com/1', 'http://example.com/2'):
        assert data_url in data_urls

    ## bad requests
    update_payload = {'dat': ''}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 400
    assert not data

    update_payload = {'dataset': {'title': 'A title'}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{10**9}/update',
                                     update_payload)
    assert status_code == 404
    assert not data

    update_payload = {'dataset': {'tags': 'asd'}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 400
    assert not data


    update_payload = {'dataset': {'tags': [{'bad_tag': 'asd'}]}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 400
    assert not data
