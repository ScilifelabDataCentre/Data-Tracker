"""Dataset requests."""
import flask

import user
import utils

blueprint = flask.Blueprint("dataset", __name__)  # pylint: disable=invalid-name


@blueprint.route("", methods=["GET"])
def list_datasets():
    """Provide a simplified list of all available datasets."""
    results = list(
        flask.g.db["datasets"].find(projection={"title": 1, "_id": 1, "tags": 1, "properties": 1})
    )
    return utils.response_json({"datasets": results})


@blueprint.route("/user", methods=["GET"])
@user.login_required
def list_user_data():
    """List all datasets belonging to current user."""
    user_orders = list(
        flask.g.db["orders"].find({"editors": flask.session["user_id"]}, {"datasets": 1})
    )
    uuids = list(ds for entry in user_orders for ds in entry["datasets"])
    user_datasets = list(flask.g.db["datasets"].find({"_id": {"$in": uuids}}))

    return utils.response_json({"datasets": user_datasets})


@blueprint.route("/<identifier>", methods=["GET"])
def get_dataset(identifier):
    """
    Retrieve the dataset with uuid <identifier>.

    Args:
        identifier (str): uuid for the wanted dataset

    Returns:
        flask.Response: json structure for the dataset
    """
    result = build_dataset_info(identifier)
    if not result:
        return flask.Response(status=404)
    return utils.response_json({"dataset": result})


@blueprint.route("/<identifier>", methods=["DELETE"])
@user.login_required
def delete_dataset(identifier: str):
    """
    Delete a dataset.

    Can be deleted only by editors or user with DATA_MANAGEMENT permissions.

    Args:
        identifier (str): The dataset uuid.
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    ds = utils.req_get_entry("datasets", identifier)
    if not ds:
        flask.abort(status=404)

    # permission check
    order = flask.g.db["orders"].find_one({"datasets": ds["_id"]})
    if not order:
        flask.current_app.logger.error("Dataset without parent order: %s", ds["_id"])
        flask.current_app.logger.error(ds)
    # permission check
    if (
        not utils.req_has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in order["editors"]
    ):
        flask.abort(status=403)

    result = utils.req_commit_to_db("datasets", "delete", {"_id": ds["_id"]})
    if not result.log or not result.data:
        flask.abort(status=500)

    collections = list(flask.g.db["collections"].find({"datasets": ds["_id"]}))
    flask.g.db["collections"].update_many({}, {"$pull": {"datasets": ds["_id"]}})
    for collection in collections:
        collection["datasets"] = [collection["datasets"].remove(ds["_id"])]
        utils.req_make_log_new(
            data_type="collection",
            action="edit",
            comment="Dataset deleted",
            data=collection,
        )

    flask.g.db["orders"].update_many({}, {"$pull": {"datasets": ds["_id"]}})
    order["datasets"].remove(ds["_id"])
    utils.req_make_log_new(
        data_type="order",
        action="edit",
        comment="Dataset deleted",
        data=order,
    )

    return flask.Response(status=200)


@blueprint.route("/<identifier>", methods=["PATCH"])
@user.login_required
def update_dataset(identifier):
    """
    Update a dataset with new values.

    Args:
        identifier (str): uuid for the wanted dataset

    Returns:
        flask.Response: success: 200, failure: 400
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    dataset = utils.req_get_entry("datasets", identifier)
    if not dataset:
        flask.abort(status=404)
    # permissions
    order = flask.g.db["orders"].find_one({"datasets": dataset["_id"]})
    if (
        not utils.req_has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in order["editors"]
    ):
        flask.abort(status=403)

    jsondata = flask.request.json
    if not jsondata or "dataset" not in jsondata or not isinstance(jsondata["dataset"], dict):
        flask.abort(status=400)
    indata = jsondata["dataset"]

    validation = utils.basic_check_indata(indata, dataset, prohibited=("_id"))
    if not validation.result:
        flask.abort(status=validation.status)

    indata = utils.prepare_for_db(indata)

    is_different = False
    for field in indata:
        if indata[field] != dataset[field]:
            is_different = True
            break

    dataset.update(indata)

    if indata and is_different:
        result = utils.req_commit_to_db("datasets", "edit", dataset)
        if not result.log or not result.data:
            flask.abort(status=500)

    return flask.Response(status=200)


@blueprint.route("/<identifier>/log", methods=["GET"])
@user.login_required
def get_dataset_log(identifier: str = None):
    """
    Get change logs for the user entry with uuid ``identifier``.

    Can be accessed by editors with DATA_EDIT and admin (DATA_MANAGEMENT).

    Logs for deleted datasets cannot be accessed.

    Args:
        identifier (str): The uuid of the dataset.

    Returns:
        flask.Response: Logs as json.
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    dataset = utils.req_get_entry("datasets", identifier)
    if not dataset:
        flask.abort(status=404)

    order_data = flask.g.db["orders"].find_one({"datasets": dataset["_id"]})
    if not order_data:
        flask.current_app.logger.error("Dataset without parent order: %s", dataset["_id"])
        flask.abort(500)

    if (
        not utils.req_has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in order_data["editors"]
    ):
        flask.abort(403)

    dataset_logs = list(
        flask.g.db["logs"].find({"data_type": "dataset", "data._id": dataset["_id"]})
    )
    for log in dataset_logs:
        del log["data_type"]

    utils.incremental_logs(dataset_logs)

    return utils.response_json(
        {"entry_id": dataset["_id"], "data_type": "dataset", "logs": dataset_logs}
    )


@blueprint.route("", methods=["POST"])
@user.login_required
def info_add_dataset():
    """Return information about the correct endpoint for adding datasets."""
    return flask.Response(
        f"Use {flask.url_for('order.add_dataset', identifier='-identifier-', _external=True)} instead",
        status=400,
    )


# helper functions
def build_dataset_info(identifier: str):
    """
    Query for a dataset from the database.

    Args:
        identifier (str): The uuid of the dataset.

    Returns:
        dict: The prepared dataset entry.
    """
    dataset = utils.req_get_entry("datasets", identifier)
    if not dataset:
        return None
    order = flask.g.db["orders"].find_one({"datasets": dataset["_id"]})
    if flask.g.db.current_user:
        curr_user = flask.g.db.current_user["_id"]
    else:
        curr_user = None

    if (
        utils.req_has_permission("DATA_MANAGEMENT")
        or curr_user in order["editors"]
    ):
        dataset["order"] = {"_id": order["_id"], "title": order["title"]}
    dataset["related"] = list(
        flask.g.db["datasets"].find({"_id": {"$in": order["datasets"]}}, {"title": 1})
    )
    dataset["related"].remove({"_id": dataset["_id"], "title": dataset["title"]})
    dataset["collections"] = list(
        flask.g.db["collections"].find({"datasets": dataset["_id"]}, {"title": 1})
    )
    for field in ("editors", "generators", "authors"):
        if field == "editors" and (
            not utils.req_has_permission("DATA_MANAGEMENT")
            and curr_user not in order[field]
        ):
            continue
        dataset[field] = utils.user_uuid_data(order[field], flask.g.db)

    dataset["organisation"] = utils.user_uuid_data(order["organisation"], flask.g.db)
    dataset["organisation"] = dataset["organisation"][0] if dataset["organisation"] else ""
    return dataset
