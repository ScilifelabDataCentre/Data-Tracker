"""Collection requests."""
import flask

import structure
import user
import utils

blueprint = flask.Blueprint("collection", __name__)  # pylint: disable=invalid-name


@blueprint.route("", methods=["GET"])
def list_collection():
    """Provide a simplified list of all available collections."""
    results = list(
        flask.g.db["collections"].find(
            projection={"title": 1, "_id": 1, "tags": 1, "properties": 1}
        )
    )
    return utils.response_json({"collections": results})


@blueprint.route("/<identifier>", methods=["GET"])
def get_collection(identifier):
    """
    Retrieve the collection with uuid <identifier>.

    Args:
        identifier (str): uuid for the wanted collection

    Returns:
        flask.Request: json structure for the collection

    """
    try:
        uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    result = flask.g.db["collections"].find_one({"_id": uuid})
    if not result:
        return flask.Response(status=404)

    # only show owner if owner/admin
    if not flask.g.current_user or (
        not user.has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in result["editors"]
    ):
        flask.current_app.logger.debug(
            "Not allowed to access editors field %s", flask.g.current_user
        )
        del result["editors"]
    else:
        result["editors"] = utils.user_uuid_data(result["editors"], flask.g.db)

    # return {_id, _title} for datasets
    result["datasets"] = [
        flask.g.db.datasets.find_one({"_id": dataset}, {"title": 1})
        for dataset in result["datasets"]
    ]

    return utils.response_json({"collection": result})


@blueprint.route("", methods=["POST"])
@user.login_required
def add_collection():
    """
    Add a collection.

    Returns:
        flask.Response: Json structure with the ``_id`` of the collection.
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    # create new collection
    collection = structure.collection()

    jsondata = flask.request.json
    if "collection" not in jsondata or not isinstance(jsondata["collection"], dict):
        flask.abort(status=400)
    indata = jsondata["collection"]

    # indata validation
    validation = utils.basic_check_indata(indata, collection, prohibited=["_id"])
    if not validation.result:
        flask.abort(status=validation.status)

    # add current user to editors if no editors are defined
    if not indata.get("editors"):
        indata["editors"] = [flask.g.current_user["_id"]]

    # convert entries to uuids
    for field in ("datasets", "editors"):
        if field in indata:
            indata[field] = [utils.str_to_uuid(value) for value in indata[field]]

    collection["description"] = utils.secure_description(collection["description"])

    collection.update(indata)

    # add to db
    result = utils.req_commit_to_db("collections", "add", collection)
    if not result.log or not result.data:
        flask.abort(status=500)

    return utils.response_json({"_id": result.ins_id})


@blueprint.route("/<identifier>", methods=["DELETE"])
@user.login_required
def delete_collection(identifier: str):
    """
    Delete a collection.

    Can be deleted only by an owner or user with DATA_MANAGEMENT permissions.

    Args:
        identifier (str): The collection uuid.
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    entry = utils.req_get_entry("collections", identifier)
    if not entry:
        flask.abort(status=404)

    # permission check
    if (
        not utils.req_check_permissions(["DATA_MANAGEMENT"])
        and flask.g.current_user["_id"] not in entry["editors"]
    ):
        flask.abort(status=403)

    result = utils.req_commit_to_db("collections", "delete", {"_id": entry["_id"]})
    if not result.log or not result.data:
        flask.abort(status=500)
    return flask.Response(status=200)


@blueprint.route("/<identifier>", methods=["PATCH"])
@user.login_required
def update_collection(identifier):
    """
    Update a collection.

    Args:
        identifier (str): The collection uuid.

    Returns:
        flask.Response: Status code.
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    collection = utils.req_get_entry("collections", identifier)
    if not collection:
        flask.abort(status=404)

    jsondata = flask.request.json
    if "collection" not in jsondata or not isinstance(jsondata["collection"], dict):
        flask.abort(status=400)
    indata = jsondata["collection"]

    # permission check
    if (
        not utils.req_check_permissions(["DATA_MANAGEMENT"])
        and flask.g.current_user["_id"] not in collection["editors"]
    ):
        flask.current_app.logger.debug(
            "Unauthorized update attempt (collection %s, user %s)",
            collection["_id"],
            flask.g.current_user["_id"],
        )
        flask.abort(status=403)

    # indata validation
    validation = utils.basic_check_indata(indata, collection, prohibited=["_id"])
    if not validation.result:
        flask.abort(status=validation.status)

    # convert entries to uuids
    for field in ("datasets", "editors"):
        if field in indata:
            indata[field] = [utils.str_to_uuid(value) for value in indata[field]]

    if "description" in indata:
        indata["description"] = utils.secure_description(indata["description"])

    is_different = False
    for field in indata:
        if indata[field] != collection[field]:
            is_different = True
            break

    flask.current_app.logger.error(indata)
    if indata and is_different:
        collection.update(indata)
        result = utils.req_commit_to_db("collections", "edit", collection)
        if not result.log or not result.data:
            flask.abort(status=500)

    return flask.Response(status=200)


@blueprint.route("/user", methods=["GET"])
@user.login_required
def list_user_collections():  # pylint: disable=too-many-branches
    """
    List collection owned by the user.

    Returns:
        flask.Response: JSON structure.
    """
    results = list(
        flask.g.db["collections"].find({"editors": flask.g.current_user["_id"]})
    )
    return utils.response_json({"collections": results})


@blueprint.route("/<identifier>/log", methods=["GET"])
@user.login_required
def get_collection_log(identifier: str = None):
    """
    Get change logs for the user entry with uuid ``identifier``.

    Can be accessed by owners and admin (DATA_MANAGEMENT).

    Args:
        identifier (str): The uuid of the collection.

    Returns:
        flask.Response: Logs as json.
    """
    try:
        collection_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    if not user.has_permission("DATA_MANAGEMENT"):
        collection_data = flask.g.db["collections"].find_one({"_id": collection_uuid})
        if not collection_data:
            flask.abort(403)
        if flask.g.current_user["_id"] not in collection_data["editors"]:
            flask.abort(403)

    collection_logs = list(
        flask.g.db["logs"].find(
            {"data_type": "collection", "data._id": collection_uuid}
        )
    )

    for log in collection_logs:
        del log["data_type"]

    utils.incremental_logs(collection_logs)

    return utils.response_json(
        {
            "entry_id": collection_uuid,
            "data_type": "collection",
            "logs": collection_logs,
        }
    )
