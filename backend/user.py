"""
User profile, permissions, and login/logout functions and endpoints.

Decorators
    Decorators used to e.g. assert that a user is logged in.

Helper functions
    Functions to help with user-related tasks, e.g. setting all variables at login.

Requests
    User-related API endpoints, including login/logout and user manament.
"""
import functools

import flask

import structure
import utils

blueprint = flask.Blueprint("user", __name__)  # pylint: disable=invalid-name

PERMISSIONS = {
    "DATA_EDIT": ("DATA_EDIT", "USER_ADD", "USER_SEARCH"),
    "DATA_LIST": ("DATA_LIST"),
    "STATISTICS": ("STATISTICS"),
    "OWNERS_READ": ("OWNERS_READ",),
    "USER_ADD": ("USER_ADD",),
    "USER_SEARCH": ("USER_SEARCH",),
    "USER_MANAGEMENT": ("USER_MANAGEMENT", "USER_ADD", "USER_SEARCH"),
    "DATA_MANAGEMENT": ("DATA_EDIT", "OWNERS_READ", "DATA_MANAGEMENT"),
}


# Decorators
def login_required(func):
    """
    Confirm that the user is logged in.

    Otherwise abort with status 401 Unauthorized.
    """

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if not flask.g.current_user:
            flask.abort(status=401)
        return func(*args, **kwargs)

    return wrap


# requests
@blueprint.route("/permissions")
def get_permission_info():
    """Get a list of all permission types."""
    return utils.response_json({"permissions": list(PERMISSIONS.keys())})


@blueprint.route("")
@login_required
def list_users():
    """
    List all users.

    Admin access should be required.
    """
    if not utils.req_has_permission("USER_SEARCH"):
        flask.abort(403)

    fields = {"api_key": 0, "api_salt": 0}

    if not utils.req_has_permission("USER_MANAGEMENT"):
        fields["auth_ids"] = 0
        fields["permissions"] = 0

    result = tuple(flask.g.db["users"].find(projection=fields))

    return utils.response_json({"users": result})


# requests
@blueprint.route("/me")
def get_current_user_info():
    """
    List basic information about the current user.

    Returns:
        flask.Response: json structure for the user
    """
    data = flask.g.current_user
    outstructure = {
        "_id": "",
        "affiliation": "",
        "auth_ids": [],
        "email": "",
        "contact": "",
        "name": "",
        "orcid": "",
        "permissions": [],
        "url": "",
    }
    if data:
        for field in outstructure:
            if field in data:
                outstructure[field] = data[field]
    return utils.response_json({"user": outstructure})


# requests
@blueprint.route("/<identifier>/apikey", methods=["POST"])
@login_required
def gen_new_api_key(identifier: str = None):
    """
    Generate a new API key for the provided or current user.

    Args:
        identifier (str): The uuid of the user.

    Returns:
        flask.Response: The new API key
    """
    if identifier != str(flask.g.current_user["_id"]) and not utils.req_has_permission(
        "USER_MANAGEMENT"
    ):
        flask.abort(403)
    try:
        user_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)
    if not (
        user_data := flask.g.db["users"].find_one({"_id": user_uuid})
    ):  # pylint: disable=superfluous-parens
        flask.abort(status=404)

    apikey = utils.gen_api_key()
    new_hash = utils.gen_api_key_hash(apikey.key, apikey.salt)
    new_values = {"api_key": new_hash, "api_salt": apikey.salt}
    user_data.update(new_values)
    result = flask.g.db["users"].update_one({"_id": user_data["_id"]}, {"$set": new_values})
    if not result.acknowledged:
        flask.current_app.logger.error("Updating API key for user %s failed", user_data["_id"])
        flask.Response(status=500)
    else:
        utils.make_log("user", "edit", "New API key", user_data)

    return utils.response_json({"key": apikey.key})


@blueprint.route("/<identifier>", methods=["GET"])
@login_required
def get_user_data(identifier: str):
    """
    Get information about a user.

    Args:
        identifier (str): The uuid of the user.

    Returns:
        flask.Response: Information about the user as json.
    """
    if not utils.req_has_permission("USER_MANAGEMENT"):
        flask.abort(403)

    try:
        user_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    if not (
        user_info := flask.g.db["users"].find_one({"_id": user_uuid})
    ):  # pylint: disable=superfluous-parens
        flask.abort(status=404)

    # The hash and salt should never leave the system
    del user_info["api_key"]
    del user_info["api_salt"]

    return utils.response_json({"user": user_info})


@blueprint.route("", methods=["POST"])
@login_required
def add_user():
    """
    Add a user.

    Returns:
        flask.Response: Information about the user as json.
    """
    if not utils.req_has_permission("USER_ADD"):
        flask.abort(403)

    new_user = structure.user()
    jsondata = flask.request.json
    if not jsondata.get("user") or not isinstance(jsondata["user"], dict):
        flask.abort(status=400)
    indata = jsondata["user"]

    validation = utils.basic_check_indata(
        indata, new_user, ("_id", "api_key", "api_salt", "auth_ids")
    )
    if not validation.result:
        flask.abort(status=validation.status)

    indata = utils.prepare_for_db(indata)
    if not indata:
        flask.abort(status=400)

    if "email" not in indata:
        flask.current_app.logger.debug("Email must be set")
        flask.abort(status=400)

    old_user = flask.g.db["users"].find_one({"email": indata["email"]})
    if old_user:
        flask.current_app.logger.debug("User already exists")
        flask.abort(status=400)

    if not utils.req_has_permission("USER_MANAGEMENT") and "permissions" in indata:
        flask.current_app.logger.debug("USER_MANAGEMENT required for permissions")
        flask.abort(403)

    new_user.update(indata)

    new_user["auth_ids"] = [new_user["email"]]

    result = utils.req_commit_to_db("users", "add", new_user)
    if not result.log or not result.data:
        flask.abort(status=500)

    return utils.response_json({"_id": result.ins_id})


@blueprint.route("/<identifier>", methods=["DELETE"])
@login_required
def delete_user(identifier: str):
    """
    Delete a user.

    Args:
        identifier (str): The uuid of the user to modify.

    Returns:
        flask.Response: Response code.
    """
    perm_status = utils.req_check_permissions(["USER_MANAGEMENT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    user_info = utils.req_get_entry("users", identifier)
    if not user_info:
        flask.abort(status=404)

    result = utils.req_commit_to_db("users", "delete", {"_id": user_info["_id"]})
    if not result.log or not result.data:
        flask.abort(status=500)

    return flask.Response(status=200)


@blueprint.route("/me", methods=["PATCH"])
@login_required
def update_current_user_info():
    """
    Update the information about the current user.

    Returns:
        flask.Response: Response code.
    """
    user_data = flask.g.current_user

    jsondata = flask.request.json
    if not jsondata.get("user") or not isinstance(jsondata["user"], dict):
        flask.abort(status=400)
    indata = jsondata["user"]
    validation = utils.basic_check_indata(
        indata,
        user_data,
        ("_id", "api_key", "api_salt", "auth_ids", "email", "permissions"),
    )
    if not validation.result:
        flask.abort(status=validation.status)

    is_different = False
    for field in indata:
        if indata[field] != user_data[field]:
            is_different = True
            break
    user_data.update(indata)

    if is_different:
        result = utils.req_commit_to_db("users", "edit", user_data)
        if not result.log or not result.data:
            flask.abort(status=500)

    return flask.Response(status=200)


@blueprint.route("/<identifier>", methods=["PATCH"])
@login_required
def update_user_info(identifier: str):
    """
    Update the information about a user.

    Requires USER_MANAGEMENT.

    Args:
        identifier (str): The uuid of the user to modify.

    Returns:
        flask.Response: Response code.
    """
    perm_status = utils.req_check_permissions(["USER_MANAGEMENT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    user_data = utils.req_get_entry("users", identifier)
    if not user_data:
        flask.abort(status=404)

    jsondata = flask.request.json
    if not jsondata.get("user") or not isinstance(jsondata["user"], dict):
        flask.abort(status=400)
    indata = jsondata["user"]

    validation = utils.basic_check_indata(
        indata, user_data, ("_id", "api_key", "api_salt", "auth_ids")
    )
    if not validation.result:
        flask.abort(status=validation.status)

    if "email" in indata:
        old_user = flask.g.db["users"].find_one({"email": indata["email"]})
        if old_user.get("_id") != user_data["_id"]:
            flask.current_app.logger.debug("User already exists")
            flask.abort(status=409)

    # Avoid "updating" and making log if there are no changes
    is_different = False
    for field in indata:
        if indata[field] != user_data[field]:
            is_different = True
            break
    user_data.update(indata)

    if is_different:
        result = utils.req_commit_to_db("users", "edit", user_data)
        if not result.log or not result.data:
            flask.abort(status=500)

    return flask.Response(status=200)


@blueprint.route("/<identifier>/log", methods=["GET"])
@login_required
def get_user_log(identifier: str):
    """
    Get change logs for the user entry with uuid ``identifier``.

    Can be accessed by actual user and admin (USER_MANAGEMENT).

    Args:
        identifier (str): The uuid of the user.

    Returns:
        flask.Response: Information about the user as json.
    """
    if str(flask.g.current_user["_id"]) != identifier and not utils.req_has_permission(
        "USER_MANAGEMENT"
    ):
        flask.abort(403)

    try:
        user_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    user_logs = list(flask.g.db["logs"].find({"data_type": "user", "data._id": user_uuid}))

    for log in user_logs:
        del log["data_type"]

    utils.incremental_logs(user_logs)

    return utils.response_json({"entry_id": user_uuid, "data_type": "user", "logs": user_logs})


@blueprint.route("/<identifier>/actions", methods=["GET"])
@login_required
def get_user_actions(identifier: str):
    """
    Get a list of actions (changes) by the user entry with uuid ``identifier``.

    Can be accessed by actual user and admin (USER_MANAGEMENT).

    Args:
        identifier (str): The uuid of the user.

    Returns:
        flask.Response: Information about the user as json.
    """
    if identifier == "me":
        identifier = str(flask.g.current_user["_id"])

    if str(flask.g.current_user["_id"]) != identifier and not utils.req_has_permission(
        "USER_MANAGEMENT"
    ):
        flask.abort(403)

    try:
        user_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    # only report a list of actions, not the actual data
    user_logs = list(flask.g.db["logs"].find({"user": user_uuid}, {"user": 0}))

    for entry in user_logs:
        entry["entry_id"] = entry["data"]["_id"]
        del entry["data"]

    return utils.response_json({"logs": user_logs})


# helper functions
def add_new_user(user_info: dict):
    """
    Add a new user to the database from first oidc login.

    First check if user with the same email exists.
    If so, add the auth_id to the user.

    Args:
        user_info (dict): Information about the user
    """
    db_user = flask.g.db["users"].find_one({"email": user_info["email"]})
    if db_user:
        db_user["auth_ids"].append(user_info["auth_id"])
        result = flask.g.db["users"].update_one(
            {"email": user_info["email"]}, {"$set": {"auth_ids": db_user["auth_ids"]}}
        )
        if not result.acknowledged:
            flask.current_app.logger.error(
                "Failed to add new auth_id to user with email %s", user_info["email"]
            )
            flask.Response(status=500)
        else:
            utils.make_log("user", "edit", "Add OIDC entry to auth_ids", db_user, no_user=True)

    else:
        new_user = structure.user()
        new_user["email"] = user_info["email"]
        new_user["name"] = user_info["name"]
        new_user["auth_ids"] = [user_info["auth_id"]]

        result = flask.g.db["users"].insert_one(new_user)
        if not result.acknowledged:
            flask.current_app.logger.error(
                "Failed to add user with email %s via oidc", user_info["email"]
            )
            flask.Response(status=500)
        else:
            utils.make_log("user", "add", "Creating new user from OAuth", new_user, no_user=True)


def do_login(auth_id: str):
    """
    Set all relevant variables for a logged in user.

    Args:
        auth_id (str): Authentication id for the user.

    Returns bool: Whether the login succeeded.
    """
    user = flask.g.db["users"].find_one({"auth_ids": auth_id})

    if not user:
        return False

    flask.session["user_id"] = user["_id"]
    flask.session.permanent = True  # pylint: disable=assigning-non-slot
    return True


def get_current_user():
    """
    Get the current user.

    Returns:
        dict: The current user.
    """
    return get_user(user_uuid=flask.session.get("user_id"))


def get_user(user_uuid=None):
    """
    Get information about the user.

    Args:
        user_uuid (str): The identifier (uuid) of the user.

    Returns:
        dict: The current user.
    """
    if user_uuid:
        user = flask.g.db["users"].find_one({"_id": user_uuid})
        if user:
            return user
    return None
