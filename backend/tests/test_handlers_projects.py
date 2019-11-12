"""Tests for the project handlers."""

import requests

from helpers import as_user, dataset_for_tests, make_request


def test_list_projects_get():
    """Test ListProjects.get()"""
    session = requests.Session()
    as_user(session, 0)
    data, status_code = make_request(session, '/api/projects')
    assert status_code == 200
    assert len(data['projects']) == 6
    assert data['projects'][0]['title'] == f"Project title {data['projects'][0]['id']}"
