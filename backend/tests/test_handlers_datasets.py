"""Tests for the dataset handlers."""

import requests

from helpers import as_user, dataset_for_tests, make_request


def test_add_dataset_get():
    """Test AddDataset.get()"""
    session = requests.Session()
    expected = {'dataset': {'title': 'Title',
                            'description': 'Description',
                            'doi': 'DOI',
                            'creator': 'Creator',
                            'dmp': 'Data Management Plan',
                            'tags': [{'title': 'Tag1'}, {'title': 'Tag2'}],
                            'publications': [{'identifier': 'Publication'}],
                            'dataUrls': [{'url': 'Data Access URL', 'description': 'Description'}],
                            'projects': ['project_id']}}

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


def test_add_dataset_post_steward():
    """Test AddDataset.post()"""
    session = requests.Session()
    payload = {'dataset': {'title': 'An added Dataset1',
                           'description': 'Description of added dataset1',
                           'doi': 'A doi for added dataset1',
                           'creator': 'The facility that created dataset1',
                           'dmp': 'Url to dmp for added dataset1',
                           'tags': [{'title': 'Tag Title 7'},
                                    {'title': 'Tag Title 1'},
                                    {'title': 'Tag Title 5'}],
                           'publications': [{'identifier': 'Publication title1. Journal:Year'}],
                           'dataUrls': [{'description': 'Part I', 'url': 'Data url 1a'},
                                        {'description': 'Part II', 'url': 'Data url 1b'}],
                           'projects': [2]}}

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


def test_add_dataset_post_bad():
    """Test AddDataset.post()"""
    session = requests.Session()
    payload = {'dataset': {'title': 'An added Dataset1',
                           'description': 'Description of added dataset1',
                           'doi': 'A doi for added dataset1',
                           'creator': 'The facility that created dataset1',
                           'dmp': 'Url to dmp for added dataset1',
                           'tags': [{'title': 'Tag Title 7'},
                                    {'title': 'Tag Title 1'},
                                    {'title': 'Tag Title 5'}],
                           'publications': [{'identifier': 'Publication title1. Journal:Year'}],
                           'dataUrls': [{'description': 'Part I', 'url': 'Data url 1a'},
                                        {'description': 'Part II', 'url': 'Data url 1b'}],
                           'projects': [2]}}

    ## bad requests
    as_user(session, 5)
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



def test_add_dataset_post_admin():
    """Test AddDataset.post()"""
    session = requests.Session()
    payload = {'dataset': {'title': 'An added Dataset1',
                           'description': 'Description of added dataset1',
                           'doi': 'A doi for added dataset1',
                           'creator': 'The facility that created dataset1',
                           'dmp': 'Url to dmp for added dataset1',
                           'tags': [{'title': 'Tag Title 7'},
                                    {'title': 'Tag Title 1'},
                                    {'title': 'Tag Title 5'}],
                           'publications': [{'identifier': 'Publication title1. Journal:Year'}],
                           'dataUrls': [{'description': 'Part I', 'url': 'Data url 1a'},
                                        {'description': 'Part II', 'url': 'Data url 1b'}],
                           'projects': [2]}}
    # admin
    as_user(session, 6)
    payload['dataset']['title'] = 'An added Dataset2'

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
    data, status_code = make_request(session, f'/api/dataset/{dataset_for_tests}/delete')
    assert status_code == 400
    assert not data


def test_delete_dataset_post(dataset_for_tests):
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

    payload = {'identifier': 9876543210}
    data, status_code = make_request(session,
                                     f'/api/dataset/{dataset_for_tests}/delete',
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
    """Tests for DeleteDataset.get()."""
    session = requests.Session()
    expected = {'query': {'title': 'Title',
                          'creator': 'Creator',
                          'tags': ['Tag1'],
                          'publications': ['Title. Journal:Year']}}

    for user in (0, 1, 5, 6):
        as_user(session, user)
        data, status_code = make_request(session,
                                         '/api/dataset/query')
        assert status_code == 200
        assert data == expected


def test_find_dataset_post():
    """Tests for FindDataset.post()."""
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
    assert len(data['datasets']) == 6
    for dataset in data['datasets']:
        for header in ('id', 'title', 'description', 'dmp'):
            assert header in dataset
        assert len(dataset) == 10

    payload = {'query': {'title': 'Dataset title'}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 6
    for dataset in data['datasets']:
        assert payload['query']['title'] in dataset['title']
        data, status_code = make_request(session,
                                         f'/api/dataset/{dataset["id"]}')
        assert status_code == 200

    payload = {'query': {'title': 'Dataset title',
                         'publications': ['A publication1. Journal:2011']}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 1
    for dataset in data['datasets']:
        assert payload['query']['title'] in dataset['title']
        data, status_code = make_request(session, f'/api/dataset/{dataset["id"]}')
        for pub in payload['query']['publications']:
            assert pub in [val['identifier'] for val in data['publications']]

    payload = {'query': {'tags': ['Tag Title 7']}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 2
    for dataset in data['datasets']:
        assert len(dataset) == 10
        data, status_code = make_request(session, f'/api/dataset/{dataset["id"]}')
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
    assert len(data['datasets']) == 6

    payload = {'query': {'title': 'Dataset title'}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 6
    for dataset in data['datasets']:
        assert payload['query']['title'] in dataset['title']
        data, status_code = make_request(session, f'/api/dataset/{dataset["id"]}')

    # owner
    as_user(session, 4)
    payload = {'query': {'title': 'Dataset title'}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 6

    payload = {'query': {'tags': ['Tag Title 7']}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 2
    for dataset in data['datasets']:
        data, status_code = make_request(session, f'/api/dataset/{dataset["id"]}')
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

    # admin
    as_user(session, 6)
    payload = {'query': {'title': 'Dataset title'}}
    data, status_code = make_request(session,
                                     '/api/dataset/query',
                                     payload)
    assert status_code == 200
    assert len(data['datasets']) == 6


def test_get_dataset_get():
    """Test GetDataset.get()"""
    session = requests.Session()
    # not logged in
    data, status_code = make_request(session, '/api/dataset/1')
    assert status_code == 200
    assert len(data) == 10
    assert len(data['tags']) == 5
    assert data['projects'] == [1]

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
    assert len(data) == 10

    # steward
    as_user(session, 5)
    data, status_code = make_request(session, '/api/dataset/4')
    assert status_code == 200
    assert len(data) == 10

    # admin
    as_user(session, 6)
    data, status_code = make_request(session, '/api/dataset/4')
    assert status_code == 200
    assert len(data) == 10

    # not found
    data, status_code = make_request(session, '/api/dataset/1234567')
    assert status_code == 404
    assert not data


def test_list_datasets_get():
    """Test ListDatasets.get()"""
    session = requests.Session()
    # not logged in
    as_user(session, 0)
    data, status_code = make_request(session, '/api/datasets')
    assert status_code == 200
    assert len(data['datasets']) == 6
    assert data['datasets'][0]['title'] == f"Dataset title {data['datasets'][0]['id']}"

    # normal user
    as_user(session, 1)
    data, status_code = make_request(session, '/api/datasets')
    assert status_code == 200
    assert len(data['datasets']) == 6

    # steward
    as_user(session, 5)
    data, status_code = make_request(session, '/api/datasets')
    assert status_code == 200
    assert len(data['datasets']) == 6
    assert 'Dataset title 4' in [dataset['title'] for dataset in data['datasets']]

    # admin
    as_user(session, 6)
    data, status_code = make_request(session, '/api/datasets')
    assert status_code == 200
    assert len(data['datasets']) == 6
    assert 'Dataset title 4' in [dataset['title'] for dataset in data['datasets']]


def test_update_dataset_get():
    """Test UpdateDataset.get()"""
    session = requests.Session()
    expected = {'dataset': {'title': 'Title',
                            'description': 'Description',
                            'doi': 'DOI',
                            'creator': 'Creator',
                            'dmp': 'Data Management Plan',
                            'tags': [{'title': 'Tag1'}, {'title': 'Tag2'}],
                            'publications': [{'identifier': 'Publication'}],
                            'dataUrls': [{'url': 'Data Access URL', 'description': 'Description'}]}}

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
    as_user(session, 2)
    update_payload = {'dataset': {'title': 'New title'}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 200
    assert not data
    data, status_code = make_request(session, f'/api/dataset/{ds_id}')
    assert status_code == 200
    assert data['title'] == 'New title'

    data, status_code = make_request(session, f'/api/dataset/{ds_id}')
    assert status_code == 200

    update_payload = {'dataset': {'tags': [{'title': 'Tag1'},
                                           {'title': 'NewTag1'},
                                           {'title': 'NewTag2'}]}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 200
    assert not data
    data, status_code = make_request(session, f'/api/dataset/{ds_id}')
    assert status_code == 200
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
    for update_payload in ({'dataset': {'tags': [{'bad_tag': 'asd'}]}},
                           {'dat': ''},
                           {'dataset': {'tags': 'asd'}},
                           {'dataset': {'bad_field': 'value'}}):
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

    # steward
    as_user(session, 5)
    update_payload = {'dataset': {'doi': 'special doi'}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 200
    assert not data
    data, status_code = make_request(session, f'/api/dataset/{ds_id}')
    assert status_code == 200
    assert data['doi'] == 'special doi'

    # admin
    as_user(session, 6)
    update_payload = {'dataset': {'doi': 'special doi2'}}
    data, status_code = make_request(session,
                                     f'/api/dataset/{ds_id}/update',
                                     update_payload)
    assert status_code == 200
    assert not data
    data, status_code = make_request(session, f'/api/dataset/{ds_id}')
    assert status_code == 200
    assert data['doi'] == 'special doi2'
