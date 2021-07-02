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
    entry = utils.req_get_entry("collections", identifier)
    if not entry:
        flask.abort(status=404)

    # only show editors if owner/admin
    if not flask.g.current_user or (
        not utils.req_has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in entry["editors"]
    ):
        flask.current_app.logger.debug(
            "Not allowed to access editors field %s", flask.g.current_user
        )
        del entry["editors"]
    else:
        entry["editors"] = utils.user_uuid_data(entry["editors"], flask.g.db)

    # return {_id, _title} for datasets
    entry["datasets"] = [
        flask.g.db.datasets.find_one({"_id": dataset}, {"title": 1})
        for dataset in entry["datasets"]
    ]

    return utils.response_json({"collection": entry})


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
    if not jsondata or "collection" not in jsondata or not isinstance(jsondata["collection"], dict):
        flask.abort(status=400)
    indata = jsondata["collection"]

    # indata validation
    validation = utils.basic_check_indata(indata, collection, prohibited=["_id"])
    if not validation.result:
        flask.abort(status=validation.status)

    if not indata.get("editors"):
        indata["editors"] = [flask.g.current_user["_id"]]
    # add current user if missing and only DATA_EDIT
    elif (
        not utils.req_has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in indata["editors"]
    ):
        indata["editors"].append(flask.g.current_user["_id"])

    # convert all incoming uuids to uuid.UUID
    indata = utils.prepare_for_db(indata)

    # convert entries to uuids
    for field in ("datasets", "editors"):
        if field in indata:
            indata[field] = [utils.str_to_uuid(value) for value in indata[field]]

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
        not utils.req_has_permission("DATA_MANAGEMENT")
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
    if not jsondata or "collection" not in jsondata or not isinstance(jsondata["collection"], dict):
        flask.abort(status=400)
    indata = jsondata["collection"]

    # permission check
    if (
        not utils.req_has_permission("DATA_MANAGEMENT")
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

    # DATA_EDIT may not delete itself from editors
    if (
        not utils.req_has_permission("DATA_MANAGEMENT")
        and indata.get("editors")
        and str(flask.g.current_user["_id"]) not in indata["editors"]
    ):
        flask.abort(status=400)

    # convert all incoming uuids to uuid.UUID
    indata = utils.prepare_for_db(indata)

    # convert entries to uuids
    for field in ("datasets", "editors"):
        if field in indata:
            indata[field] = [utils.str_to_uuid(value) for value in indata[field]]

    is_different = False
    for field in indata:
        if indata[field] != collection[field]:
            is_different = True
            break

    if indata and is_different:
        collection.update(indata)
        result = utils.req_commit_to_db("collections", "edit", collection)
        if not result.log or not result.data:
            flask.abort(status=500)

    return flask.Response(status=200)


@blueprint.route("/<identifier>/log", methods=["GET"])
@user.login_required
def get_collection_log(identifier: str = None):
    """
    Get change logs for the collection matching ``identifier``.

    Can be accessed by editors (with DATA_EDIT) and admin (DATA_MANAGEMENT).

    Deleted entries cannot be accessed.

    Args:
        identifier (str): The uuid of the collection.

    Returns:
        flask.Response: Logs as json.
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    collection = utils.req_get_entry("collections", identifier)
    if not collection:
        flask.abort(status=404)
    if (
        not utils.req_has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in collection["editors"]
    ):
        flask.abort(403)

    collection_logs = list(
        flask.g.db["logs"].find({"data_type": "collection", "data._id": collection["_id"]})
    )

    for log in collection_logs:
        del log["data_type"]

    utils.incremental_logs(collection_logs)

    return utils.response_json(
        {
            "entry_id": collection["_id"],
            "data_type": "collection",
            "logs": collection_logs,
        }
    )
