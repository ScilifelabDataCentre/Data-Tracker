"""Tests for the handlers in application.py."""

import json
import os
import requests


settings = json.loads(open(f'{os.path.dirname(os.path.realpath(__file__))}/settings_tests.json').read())
BASE_URL=f"{settings['host']}:{settings['port']}"

def test_list_datasets_get():
    """Test ListDatasets.get()"""
    response = requests.get(f'{BASE_URL}/api/datasets')
    data = json.loads(response.text)
    assert len(data['datasets']) == 4
    assert data['datasets'][0]['title'] == f"Dataset title {data['datasets'][0]['id']}"

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


def test_get_dataset_get():
    """Test GetDataset.get()"""
    response = requests.get(f'{BASE_URL}/api/dataset/1')
    data = json.loads(response.text)
    assert len(data) == 10
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
    response = requests.get(f'{BASE_URL}/api/dataset/5')
    data = json.loads(response.text)
    assert len(data['publications']) == 1
    assert data['publications'][0]['identifier'] == 'A publication3. Journal:2013'

    # not found
    response = requests.get(f'{BASE_URL}/api/dataset/123456')
    assert response.status_code == 404

    # bad request
    response = requests.get(f'{BASE_URL}/api/dataset/abcdef')
    assert response.status_code == 400
