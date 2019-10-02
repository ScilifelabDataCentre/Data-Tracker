"""Tests for the handlers in application.py."""

import json
import os
import requests

settings = json.loads(open(f'{os.path.dirname(os.path.realpath(__file__))}/settings_tests.json').read())
BASE_URL=f"{settings['host']}:{settings['port']}"


def test_add_dataset_post():
    """Test AddDataset.post()"""
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
                           'data_urls': [{'description': 'Part I', 'url': 'Data url 1a'},
                                         {'description': 'Part II', 'url': 'Data url 1b'}],
                           'owners': [{'email': 'user1@example.com'}],
                           'visible': True}}

    # steward
    response = requests.get(f'{BASE_URL}/developer/login?userid=5')
    cookie_jar = response.cookies
    headers = {'X-Xsrftoken': cookie_jar['_xsrf']}

    response_post = requests.post(f'{BASE_URL}/api/dataset/add',
                                  data=json.dumps(payload),
                                  cookies=cookie_jar,
                                  headers=headers)
    assert response_post.status_code == 200
    ## TODO: better approach once search is implemented
    response = requests.get(f'{BASE_URL}/api/datasets', cookies=cookie_jar)
    data = json.loads(response.text)
    dbid = next(filter(lambda x: x['title'] == payload['dataset']['title'], data['datasets']))['id']
    response = requests.get(f'{BASE_URL}/api/dataset/{dbid}', cookies=cookie_jar)
    data = json.loads(response.text)
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
            elif header == 'data_urls':
                assert (sorted([url['url'] for url in data['dataUrls']]) ==
                        sorted([url['url'] for url in payload['dataset'][header]]))
                assert (sorted([url['description'] for url in data['dataUrls']]) ==
                        sorted([url['description'] for url in payload['dataset'][header]]))
            else:
                assert data[header] == payload['dataset'][header]

    ## bad requests
    response_post = requests.post(f'{BASE_URL}/api/dataset/add',
                                  data=json.dumps({'bad_request': None}),
                                  cookies=cookie_jar,
                                  headers=headers)
    assert response_post.status_code == 400

    response_post = requests.post(f'{BASE_URL}/api/dataset/add',
                                  data=json.dumps({'dataset': {'title_missing': None}}),
                                  cookies=cookie_jar,
                                  headers=headers)
    assert response_post.status_code == 400

    response_post = requests.post(f'{BASE_URL}/api/dataset/add',
                                  data=json.dumps({'dataset': {'title': ''}}),
                                  cookies=cookie_jar,
                                  headers=headers)
    assert response_post.status_code == 400
    
    # admin
    payload['dataset']['title'] = 'An added Dataset2'
    payload['dataset']['owners'].append({'email': 'user2@example.com'})

    response = requests.get(f'{BASE_URL}/developer/login?userid=6')
    cookie_jar = response.cookies
    response_post = requests.post(f'{BASE_URL}/api/dataset/add',
                                  data=json.dumps(payload),
                                  cookies=cookie_jar,
                                  headers={'X-Xsrftoken': cookie_jar['_xsrf']})
    assert response_post.status_code == 200
    # TODO: better approach once search is implemented
    response = requests.get(f'{BASE_URL}/api/datasets', cookies=cookie_jar)
    data = json.loads(response.text)
    dbid = next(filter(lambda x: x['title'] == payload['dataset']['title'], data['datasets']))['id']
    response = requests.get(f'{BASE_URL}/api/dataset/{dbid}', cookies=cookie_jar)
    data = json.loads(response.text)

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
            elif header == 'data_urls':
                assert (sorted([url['url'] for url in data['dataUrls']]) ==
                        sorted([url['url'] for url in payload['dataset'][header]]))
                assert (sorted([url['description'] for url in data['dataUrls']]) ==
                        sorted([url['description'] for url in payload['dataset'][header]]))
            else:
                assert data[header] == payload['dataset'][header]

    # not logged in: fail
    response = requests.get(f'{BASE_URL}/api/datasets')
    cookie_jar = response.cookies
    response_post = requests.post(f'{BASE_URL}/api/dataset/add',
                                  data=json.dumps(payload),
                                  cookies=cookie_jar,
                                  headers={'X-Xsrftoken': cookie_jar['_xsrf']})
    assert response_post.status_code == 403

    # normal user: fail
    response = requests.get(f'{BASE_URL}/developer/login?userid=1')
    cookie_jar = response.cookies
    response_post = requests.post(f'{BASE_URL}/api/dataset/add',
                                  data=json.dumps(payload),
                                  cookies=cookie_jar,
                                  headers={'X-Xsrftoken': response.cookies['_xsrf']})
    assert response_post.status_code == 403


def test_delete_dataset_post():
    """Test DeleteDataset.post()"""
    # steward
    ## will delete the dataset added as steward in test_add_dataset_post()
    response = requests.get(f'{BASE_URL}/developer/login?userid=5')
    cookie_jar = response.cookies
    headers = {'X-Xsrftoken': cookie_jar['_xsrf']}

    ## TODO: better approach once search is implemented
    response = requests.get(f'{BASE_URL}/api/datasets', cookies=cookie_jar)
    data = json.loads(response.text)
    dbid = next(filter(lambda x: x['title'] == 'An added Dataset1', data['datasets']))['id']
    payload = {'identifier': dbid}
    response_post = requests.post(f'{BASE_URL}/api/dataset/delete',
                                  data=json.dumps(payload),
                                  cookies=cookie_jar,
                                  headers=headers)
    assert response_post.status_code == 200

    ## bad requests
    payload = {'identifier': 10**7}
    response_post = requests.post(f'{BASE_URL}/api/dataset/delete',
                                  data=json.dumps(payload),
                                  cookies=cookie_jar,
                                  headers=headers)
    assert response_post.status_code == 400
    payload = {'identifier': 'abc'}
    response_post = requests.post(f'{BASE_URL}/api/dataset/delete',
                                  data=json.dumps(payload),
                                  cookies=cookie_jar,
                                  headers=headers)
    assert response_post.status_code == 400

    # admin
    ## will delete the dataset added as admin in test_add_dataset_post()
    response = requests.get(f'{BASE_URL}/developer/login?userid=6')
    cookie_jar = response.cookies
    headers = {'X-Xsrftoken': cookie_jar['_xsrf']}

    ## TODO: better approach once search is implemented
    response = requests.get(f'{BASE_URL}/api/datasets', cookies=cookie_jar)
    data = json.loads(response.text)
    dbid = next(filter(lambda x: x['title'] == 'An added Dataset2', data['datasets']))['id']
    payload = {'identifier': dbid}
    response_post = requests.post(f'{BASE_URL}/api/dataset/delete',
                                  data=json.dumps(payload),
                                  cookies=cookie_jar,
                                  headers=headers)
    assert response_post.status_code == 200

    # not logged in: fail
    response = requests.get(f'{BASE_URL}/api/datasets')
    cookie_jar = response.cookies
    headers = {'X-Xsrftoken': cookie_jar['_xsrf']}
    response_post = requests.post(f'{BASE_URL}/api/dataset/delete',
                                  data=json.dumps(payload),
                                  cookies=cookie_jar,
                                  headers=headers)
    assert response_post.status_code == 403

    # normal user: fail
    response = requests.get(f'{BASE_URL}/developer/login?userid=1')
    cookie_jar = response.cookies
    headers = {'X-Xsrftoken': cookie_jar['_xsrf']}
    response_post = requests.post(f'{BASE_URL}/api/dataset/delete',
                                  data=json.dumps(payload),
                                  cookies=cookie_jar,
                                  headers=headers)
    assert response_post.status_code == 403


def test_countrylist_get():
    """Test CountryList.get()"""
    response = requests.get(f'{BASE_URL}/api/countries')
    data = json.loads(response.text)

    assert len(data['countries']) == 240


def test_find_dataset_post():
    """Test FindDataset.post()"""
    # not logged in
    session = requests.Session()
    session.get(f'{BASE_URL}/api/datasets')
    session.headers['X-Xsrftoken'] = session.cookies['_xsrf']

    payload = {'query': {'title': 'Dataset title 2'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 1

    payload = {'query': {'title': 'Dataset title'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 4
    for dataset in data['datasets']:
        assert len(dataset) == 8

    payload = {'query': {'title': 'Dataset title',
                         'owner': 'A Name4'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 2
    for dataset in data['datasets']:
        assert payload['query']['title'] in dataset['title']
        response = session.get(f'{BASE_URL}/api/dataset/{dataset["id"]}')
        data = json.loads(response.text)
        assert payload['query']['owner'] in [val['name'] for val in data['owners']]

    payload = {'query': {'title': 'Dataset title',
                         'owner': 'A Name1',
                         'publication': 'A publication1. Journal:2011'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 1
    for dataset in data['datasets']:
        assert payload['query']['title'] in dataset['title']
        response = session.get(f'{BASE_URL}/api/dataset/{dataset["id"]}')
        data = json.loads(response.text)
        assert payload['query']['publication'] in [val['identifier'] for val in data['publications']]

    payload = {'query': {'tag': 'Tag Title 7'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 1
    for dataset in data['datasets']:
        response = session.get(f'{BASE_URL}/api/dataset/{dataset["id"]}')
        data = json.loads(response.text)
        assert payload['query']['tag'] in [val['title'] for val in data['tags']]        

    ## bad queries
    payload = {'query': {}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    assert response.status_code == 400
    payload = {'query': {'bad_type': None}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    assert response.status_code == 400

    # normal user
    session.get(f'{BASE_URL}/developer/login?userid=1)')
    session.headers['X-Xsrftoken'] = session.cookies['_xsrf']

    payload = {'query': {'title': 'Dataset title'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 4

    payload = {'query': {'title': 'Dataset title',
                         'owner': 'A Name4'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 2
    for dataset in data['datasets']:
        assert payload['query']['title'] in dataset['title']
        response = session.get(f'{BASE_URL}/api/dataset/{dataset["id"]}')
        data = json.loads(response.text)
        assert payload['query']['owner'] in [val['name'] for val in data['owners']]

    # owner
    session.get(f'{BASE_URL}/developer/login?userid=4')
    session.headers['X-Xsrftoken'] = session.cookies['_xsrf']
    payload = {'query': {'title': 'Dataset title'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 5

    payload = {'query': {'tag': 'Tag Title 7'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 2
    for dataset in data['datasets']:
        response = session.get(f'{BASE_URL}/api/dataset/{dataset["id"]}')
        data = json.loads(response.text)
        assert payload['query']['tag'] in [val['title'] for val in data['tags']]

    # steward
    session.get(f'{BASE_URL}/developer/login?userid=5')
    session.headers['X-Xsrftoken'] = session.cookies['_xsrf']

    payload = {'query': {'title': 'Dataset title'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 6
    payload = {'query': {'title': 'Dataset title',
                         'owner': 'A Name4'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 3

    # admin
    session.get(f'{BASE_URL}/developer/login?userid=6')
    session.headers['X-Xsrftoken'] = session.cookies['_xsrf']

    payload = {'query': {'title': 'Dataset title'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 6
    payload = {'query': {'title': 'Dataset title',
                         'owner': 'A Name4'}}
    response = session.post(f'{BASE_URL}/api/dataset/query',
                            data=json.dumps(payload))
    data = json.loads(response.text)
    assert len(data['datasets']) == 3


def test_get_dataset_get():
    """Test GetDataset.get()"""
    response = requests.get(f'{BASE_URL}/api/dataset/1')
    data = json.loads(response.text)
    assert len(data) == 11
    assert len(data['tags']) == 5

    tag_titles = [tag['title'] for tag in data['tags']]
    for i in [2, 3, 4, 5, 8]:
        assert f'Tag Title {i}' in tag_titles

    data_urls = [data_url['url'] for data_url in data['dataUrls']]
    for i in [1, 2]:
        assert f'https:www.example.com/url{i}' in data_urls

    # tags should be empty list if no tags
    response = requests.get(f'{BASE_URL}/api/dataset/3')
    data = json.loads(response.text)
    assert len(data['tags']) == 0

    # data_urls should be empty list if no urls
    response = requests.get(f'{BASE_URL}/api/dataset/2')
    data = json.loads(response.text)
    assert len(data['dataUrls']) == 0
    # publications should be empty list if none
    assert len(data['publications']) == 0

    # publications are retrieved correctly
    response = requests.get(f'{BASE_URL}/api/dataset/3')
    data = json.loads(response.text)
    assert len(data['publications']) == 1
    assert data['publications'][0]['identifier'] == 'A publication2. Journal:2012'

    # owned by user
    response = requests.get(f'{BASE_URL}/developer/login?userid=4')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/dataset/4', cookies=cookie_jar)
    data = json.loads(response.text)
    assert len(data) == 11

    # steward
    response = requests.get(f'{BASE_URL}/developer/login?userid=5')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/dataset/4', cookies=cookie_jar)
    assert len(data) == 11

    # admin
    response = requests.get(f'{BASE_URL}/developer/login?userid=6')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/dataset/4', cookies=cookie_jar)
    assert len(data) == 11

    # forbidden
    response = requests.get(f'{BASE_URL}/api/dataset/4')
    assert response.status_code == 403
    response = requests.get(f'{BASE_URL}/developer/login?userid=1')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/dataset/4', cookies=cookie_jar)
    assert response.status_code == 403

    # not found
    response = requests.get(f'{BASE_URL}/api/dataset/123456')
    assert response.status_code == 404


def test_get_user_get():
    """Test GetUser.get()"""
    # no user
    response = requests.get(f'{BASE_URL}/api/users/me')
    data = json.loads(response.text)
    assert data == {"user": None,
                    "email": None}

    # logged in user
    response = requests.get(f'{BASE_URL}/developer/login?userid=4')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/users/me', cookies=cookie_jar)
    data = json.loads(response.text)
    assert data == {"user": "A Name4",
                    "email": "user4@example.com",
                    "affiliation": "A University4",
                    "country": "A Country4"}


def test_list_datasets_get():
    """Test ListDatasets.get()"""
    response = requests.get(f'{BASE_URL}/api/datasets')
    data = json.loads(response.text)
    assert len(data['datasets']) == 4
    assert data['datasets'][0]['title'] == f"Dataset title {data['datasets'][0]['id']}"

    # log in as user, no extra
    response = requests.get(f'{BASE_URL}/developer/login?userid=1')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/datasets', cookies=cookie_jar)
    data = json.loads(response.text)
    assert len(data['datasets']) == 4

    # log in as user that owns dataset and list extra
    response = requests.get(f'{BASE_URL}/developer/login?userid=4')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/datasets', cookies=cookie_jar)
    data = json.loads(response.text)
    assert len(data['datasets']) == 5
    assert {"id": 4, "title": "Dataset title 4"} in data['datasets']

    # log in as steward and list extra
    response = requests.get(f'{BASE_URL}/developer/login?userid=5')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/datasets', cookies=cookie_jar)
    data = json.loads(response.text)
    assert len(data['datasets']) == 6
    assert {"id": 4, "title": "Dataset title 4"} in data['datasets']

    # log in as admin and list extra
    response = requests.get(f'{BASE_URL}/developer/login?userid=6')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/datasets', cookies=cookie_jar)
    data = json.loads(response.text)
    assert len(data['datasets']) == 6
    assert {"id": 4, "title": "Dataset title 4"} in data['datasets']
    assert {"id": 5, "title": "Dataset title 5"} in data['datasets']


def test_list_user_get():
    """Test ListUser.get()"""
    # no user - forbidden
    response = requests.get(f'{BASE_URL}/api/users')
    assert response.status_code == 403

    # normal user - forbidden
    response = requests.get(f'{BASE_URL}/developer/login?userid=1')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/users', cookies=cookie_jar)
    assert response.status_code == 403

    # Steward user - forbidden
    response = requests.get(f'{BASE_URL}/developer/login?userid=5')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/users', cookies=cookie_jar)
    assert response.status_code == 403

    # Admin user - list users
    response = requests.get(f'{BASE_URL}/developer/login?userid=6')
    cookie_jar = response.cookies
    response = requests.get(f'{BASE_URL}/api/users', cookies=cookie_jar)
    data = json.loads(response.text)
    assert len(data['users']) == 6
    assert {"id": 5,
            "name": "A Name5",
            "email": "user5@example.com",
            "authIdentity": "user5auth",
            "affiliation": "A University5",
            "country": "A Country5",
            "permission": "Steward"} in data['users']
