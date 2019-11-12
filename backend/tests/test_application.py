"""Tests for the handlers in application.py."""

import requests

from helpers import as_user, make_request


def test_countrylist_get():
    """Test CountryList.get()"""
    session = requests.Session()
    data, status_code = make_request(session, '/api/countries')
    assert status_code == 200
    assert len(data['countries']) == 240


def test_get_current_user_get():
    """Test GetCurrentUser.get()"""
    session = requests.Session()
    # not logged in
    as_user(session, 0)
    data, status_code = make_request(session, '/api/users/me')
    assert status_code == 200
    assert data == {'user': None,
                    'email': None,
                    'permission': None}

    # logged in user
    as_user(session, 4)
    data, status_code = make_request(session, '/api/users/me')
    assert status_code == 200
    assert data == {'user': 'A Name4',
                    'email': 'user4@example.com',
                    'affiliation': 'A University4',
                    'country': 'A Country4',
                    'permission': 'Standard'}


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
