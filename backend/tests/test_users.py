"""Tests for dataset requests."""
import re
import requests
import uuid

# avoid pylint errors because of fixtures
# pylint: disable = redefined-outer-name, unused-import
from helpers import (
    make_request,
    as_user,
    make_request_all_roles,
    USERS,
    mdb,
    random_string,
)


def test_list_users(mdb):
    """
    Retrieve list of users.

    Assert that USER_MANAGEMENT is required.
    """
    responses = make_request_all_roles("/api/v1/user", ret_json=True)
    for response in responses:
        if response.role in ("users", "root", "edit"):
            assert response.code == 200
            assert len(response.data["users"]) == mdb["users"].count_documents({})
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_list_info():
    """Retrieve info about current user."""
    responses = make_request_all_roles("/api/v1/user/me", ret_json=True)
    for response in responses:
        assert response.code == 200
        assert len(response.data["user"]) == 9
        if response.role != "no-login":
            assert response.data["user"]["name"] == f"{response.role.capitalize()}"


def test_update_current_user(mdb):
    """Update the info about the current user."""
    session = requests.Session()

    indata = {"user": {}}
    for user in USERS:
        as_user(session, USERS[user])
        user_info = mdb["users"].find_one({"auth_ids": USERS[user]})
        response = make_request(
            session, "/api/v1/user/me", ret_json=True, method="PATCH", data=indata
        )
        if user != "no-login":
            assert response.code == 400
        else:
            assert response.code == 401
        assert not response.data
        new_user_info = mdb["users"].find_one({"auth_ids": USERS[user]})
        assert user_info == new_user_info

    indata = {"user": {"affiliation": "Updated University", "name": "Updated name"}}
    session = requests.Session()
    for user in USERS:
        as_user(session, USERS[user])
        user_info = mdb["users"].find_one({"auth_ids": USERS[user]})
        response = make_request(
            session, "/api/v1/user/me", ret_json=True, method="PATCH", data=indata
        )
        if user != "no-login":
            assert response.code == 200
            assert not response.data
            new_user_info = mdb["users"].find_one({"auth_ids": USERS[user]})
            for key in new_user_info:
                if key in indata["user"].keys():
                    assert new_user_info[key] == indata["user"][key]
                else:
                    mdb["users"].update_one(new_user_info, {"$set": user_info})
        else:
            assert response.code == 401
            assert not response.data


def test_update_current_user_bad():
    """Update the info about the current user."""
    indata = {"user": {"_id": str(uuid.uuid4())}}
    responses = make_request_all_roles(
        "/api/v1/user/me", ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"user": {"api_key": uuid.uuid4().hex}}
    responses = make_request_all_roles(
        "/api/v1/user/me", ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"user": {"auth_ids": [uuid.uuid4().hex]}}
    responses = make_request_all_roles(
        "/api/v1/user/me", ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"user": {"email": "email@example.com"}}
    responses = make_request_all_roles(
        "/api/v1/user/me", ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"user": {"permissions": ["USER_MANAGEMENT", "DATA_MANAGEMENT"]}}
    responses = make_request_all_roles(
        "/api/v1/user/me", ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data


def test_update_user(mdb):
    """Update the info for a user."""
    user_info = mdb["users"].find_one({"auth_ids": USERS["base"]})

    indata = {}
    responses = make_request_all_roles(
        f'/api/v1/user/{user_info["_id"]}', ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role in ("users", "root"):
            assert response.code == 400
            new_user_info = mdb["users"].find_one({"auth_ids": {"$in": user_info["auth_ids"]}})
            assert user_info == new_user_info
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"user": {"affiliation": "Updated University", "name": "Updated name"}}
    session = requests.session()
    for user_type in USERS:
        as_user(session, USERS[user_type])
        response = make_request(
            session,
            f'/api/v1/user/{user_info["_id"]}',
            ret_json=True,
            method="PATCH",
            data=indata,
        )
        if user_type in ("users", "root"):
            assert response.code == 200
            assert not response.data
            new_user_info = mdb["users"].find_one({"auth_ids": user_info["auth_ids"]})
            for key in indata["user"]:
                assert new_user_info[key] == indata["user"][key]
            mdb["users"].update_one(new_user_info, {"$set": user_info})
        elif user_type == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_update_user_bad(mdb):
    """
    Update the info for a user.

    Bad requests.
    """
    user_info = mdb["users"].find_one({"auth_ids": USERS["base"]})

    indata = {"user": {"_id": str(uuid.uuid4())}}
    responses = make_request_all_roles(
        f'/api/v1/user/{user_info["_id"]}', ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"user": {"api_key": uuid.uuid4().hex}}
    responses = make_request_all_roles(
        f'/api/v1/user/{user_info["_id"]}', ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"user": {"email": "bad@email"}}
    responses = make_request_all_roles(
        f'/api/v1/user/{user_info["_id"]}', ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role in ("users", "root"):
            assert response.code == 400
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"user": {}}
    responses = make_request_all_roles(
        f"/api/v1/user/{uuid.uuid4()}", ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role in ("users", "root"):
            assert response.code == 404
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data

    indata = {"user": {}}
    responses = make_request_all_roles(
        f"/api/v1/user/{random_string()}", ret_json=True, method="PATCH", data=indata
    )
    for response in responses:
        if response.role in ("users", "root"):
            assert response.code == 404
        elif response.role == "no-login":
            assert response.code == 401
        else:
            assert response.code == 403
        assert not response.data


def test_add_user(mdb):
    """Add a user."""
    indata = {"user": {"email": "new_user@added.example.com"}}
    session = requests.Session()
    for role in USERS:
        as_user(session, USERS[role])
        response = make_request(session, "/api/v1/user", ret_json=True, method="POST", data=indata)
        if role in ("users", "root", "edit"):
            assert response.code == 200
            assert "id" in response.data
            new_user_info = mdb["users"].find_one({"_id": uuid.UUID(response.data["id"])})
            assert indata["user"]["email"] == new_user_info["email"]
            indata["user"]["email"] = "new_" + indata["user"]["email"]
        elif role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data

    indata = {"user": {
        "affiliation": "Added University",
        "name": "Added name",
        "email": "user2@added.example.com",
        "permissions": ["DATA_EDIT"],
    }}
    session = requests.session()
    as_user(session, USERS["edit"])
    response = make_request(session, "/api/v1/user", ret_json=True, method="POST", data=indata)
    assert response.code == 403

    as_user(session, USERS["root"])
    response = make_request(session, "/api/v1/user", ret_json=True, method="POST", data=indata)
    assert response.code == 200
    assert "id" in response.data
    new_user_info = mdb["users"].find_one({"_id": uuid.UUID(response.data["id"])})
    for key in indata["user"]:
        assert new_user_info[key] == indata["user"][key]


def test_delete_user(mdb):
    """Test deleting users (added when testing to add users)"""
    re_users = re.compile("@added.example.com")
    users = list(mdb["users"].find({"email": re_users}, {"_id": 1}))
    if not users:
        assert False
    session = requests.Session()
    i = 0
    while i < len(users):
        for role in USERS:
            as_user(session, USERS[role])
            response = make_request(session, f'/api/v1/user/{users[i]["_id"]}', method="DELETE")
            if role in ("users", "root"):
                assert response.code == 200
                assert not response.data
                assert not mdb["users"].find_one({"_id": users[i]["_id"]})
                assert mdb["logs"].find_one(
                    {
                        "data._id": users[i]["_id"],
                        "action": "delete",
                        "data_type": "user",
                    }
                )
                i += 1
                if i >= len(users):
                    break
            elif role == "no-login":
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data


def test_key_reset(mdb):
    """Test generation of new API keys"""
    mod_user = {"auth_ids": "facility18::local"}
    mod_user_info = mdb.users.find_one(mod_user)

    session = requests.Session()
    for userid in USERS:
        as_user(session, USERS[userid])
        if userid != "no-login":
            # Test modifying user's own key
            user_response = make_request(session, "/api/v1/user/me", method="GET", ret_json=True)
            response = make_request(
                session,
                f"/api/v1/user/{user_response.data['user']['id']}/apikey",
                method="POST",
                ret_json=True,
            )
            assert response.data["key"]
            assert response.code == 200
            new_key = response.data["key"]
            response = make_request(
                session,
                "/api/v1/login/apikey",
                data={"api-user": USERS[userid], "api-key": new_key},
                method="POST",
            )
            assert response.code == 200
            assert not response.data

        response = make_request(
            session, f'/api/v1/user/{mod_user_info["_id"]}/apikey', method="POST"
        )
        if userid not in ("users", "root"):
            if userid == "no-login":
                assert response.code == 401
                assert not response.data
            else:
                assert response.code == 403
                assert not response.data
        else:
            assert response.code == 200
            new_key = response.data["key"]
            response = make_request(
                session,
                "/api/v1/login/apikey",
                data={"api-user": mod_user["auth_ids"], "api-key": new_key},
                method="POST",
            )
            user_response = make_request(session, "/api/v1/user/me", method="GET", ret_json=True)
            assert mod_user["auth_ids"] in user_response.data["user"]["auth_ids"]
            assert response.code == 200
            assert not response.data


def test_get_user_logs_permissions(mdb):
    """
    Get user logs.

    Assert that USER_MANAGEMENT or actual user is required.
    """
    user_uuid = mdb["users"].find_one({"auth_ids": USERS["base"]}, {"_id": 1})["_id"]
    responses = make_request_all_roles(f"/api/v1/user/{user_uuid}/log", ret_json=True)
    for response in responses:
        if response.role in ("base", "users", "root"):
            assert response.code == 200
            assert "logs" in response.data
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data


def test_get_user_logs(mdb):
    """
    Request the logs for multiple users.

    Confirm that the logs contain only the intended fields.
    """
    session = requests.session()
    users = mdb["users"].aggregate([{"$sample": {"size": 2}}])
    for user in users:
        logs = list(mdb["logs"].find({"data_type": "user", "data._id": user["_id"]}))
        as_user(session, USERS["users"])
        response = make_request(session, f'/api/v1/user/{user["_id"]}/log', ret_json=True)
        assert response.data["data_type"] == "user"
        assert response.data["entry_id"] == str(user["_id"])
        assert len(response.data["logs"]) == len(logs)
        assert response.code == 200


def test_get_user_actions_access(mdb):
    """
    Get user logs.

    Assert that USER_MANAGEMENT or actual user is required.
    """
    user_uuid = mdb["users"].find_one({"auth_ids": USERS["base"]}, {"_id": 1})["_id"]
    responses = make_request_all_roles(f"/api/v1/user/{user_uuid}/actions", ret_json=True)
    for response in responses:
        if response.role in ("base", "users", "root"):
            assert response.code == 200
            assert "logs" in response.data
        elif response.role == "no-login":
            assert response.code == 401
            assert not response.data
        else:
            assert response.code == 403
            assert not response.data
