"""Tests for logins."""
import requests

import helpers

# pylint: disable=redefined-outer-name


def test_logout():
    """Assure that session is cleared after logging out."""
    session = requests.Session()
    helpers.as_user(session, helpers.USERS["root"])
    response = helpers.make_request(session, "/api/v1/user/me")
    for field in response.data["user"]:
        assert response.data["user"][field]
    response = helpers.make_request(session, "/api/v1/logout", ret_json=False)
    response = helpers.make_request(session, "/api/v1/user/me")
    for field in response.data["user"]:
        assert not response.data["user"][field]


def test_key_login():
    """Test API key login for all users"""
    session = requests.Session()
    helpers.as_user(session, None)
    for i, userid in enumerate(helpers.USERS):
        response = helpers.make_request(
            session,
            "/api/v1/login/apikey",
            data={"api-user": helpers.USERS[userid], "api-key": str(i - 1)},
            method="POST",
        )
        if userid == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 200
            assert not response.data

            response = helpers.make_request(session, "/api/v1/developer/loginhello")
            assert response.code == 200
            assert response.data == {"test": "success"}


def test_list_login_types():
    """List possible ways to login"""
    responses = helpers.make_request_all_roles("/api/v1/login", ret_json=True)
    for response in responses:
        assert response.code == 200
        assert response.data == {"types": ["apikey", "oidc"]}


def test_list_oidc_types():
    """List supported oidc logins"""
    responses = helpers.make_request_all_roles("/api/v1/login/oidc", ret_json=True)
    for response in responses:
        assert response.code == 200
        assert response.data == {"entry": "/api/v1/login/oidc/entry"}
