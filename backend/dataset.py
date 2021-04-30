"""Dataset requests."""
import flask

import structure
import utils
import user

blueprint = flask.Blueprint("dataset", __name__)  # pylint: disable=invalid-name


@blueprint.route("", methods=["GET"])
def list_datasets():
    """Provide a simplified list of all available datasets."""
    results = list(
        flask.g.db["datasets"].find(
            projection={"title": 1, "_id": 1, "tags": 1, "properties": 1}
        )
    )
    return utils.response_json({"datasets": results})


@blueprint.route("/user", methods=["GET"])
@user.login_required
def list_user_data():
    """List all datasets belonging to current user."""
    user_orders = list(
        flask.g.db["orders"].find(
            {"editors": flask.session["user_id"]}, {"datasets": 1}
        )
    )
    uuids = list(ds for entry in user_orders for ds in entry["datasets"])
    user_datasets = list(flask.g.db["datasets"].find({"_id": {"$in": uuids}}))

    return utils.response_json({"datasets": user_datasets})


@blueprint.route("/structure", methods=["GET"])
def get_dataset_data_structure():
    """
    Get an empty dataset entry.

    Returns:
        flask.Response: JSON structure with a list of datasets.
    """
    empty_dataset = structure.dataset()
    empty_dataset["_id"] = ""
    return utils.response_json({"dataset": empty_dataset})


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
    try:
        ds_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)
    dataset = flask.g.db["datasets"].find_one({"_id": ds_uuid})
    if not dataset:
        flask.abort(status=404)

    # permission check
    order = flask.g.db["orders"].find_one({"datasets": ds_uuid})
    if (
        not user.has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in order["editors"]
    ):
        flask.abort(status=403)

    result = flask.g.db["datasets"].delete_one({"_id": ds_uuid})
    if not result.acknowledged:
        flask.current_app.logger.error("Failed to delete dataset %s", ds_uuid)
        return flask.Response(status=500)
    utils.make_log("dataset", "delete", "Deleted dataset", data={"_id": ds_uuid})

    for entry in flask.g.db["orders"].find({"datasets": ds_uuid}):
        result = flask.g.db["orders"].update_one(
            {"_id": entry["_id"]}, {"$pull": {"datasets": ds_uuid}}
        )
        if not result.acknowledged:
            flask.current_app.logger.error(
                "Failed to delete dataset %s in order %s", ds_uuid, entry["_id"]
            )
            return flask.Response(status=500)
        new_data = flask.g.db["orders"].find_one({"_id": entry["_id"]})
        utils.make_log("order", "edit", f"Deleted dataset {ds_uuid}", new_data)

    for entry in flask.g.db["collections"].find({"datasets": ds_uuid}):
        flask.g.db["collections"].update_one(
            {"_id": entry["_id"]}, {"$pull": {"datasets": ds_uuid}}
        )
        if not result.acknowledged:
            flask.current_app.logger.error(
                "Failed to delete dataset %s in project %s", ds_uuid, entry["_id"]
            )
            return flask.Response(status=500)
        new_data = flask.g.db["collections"].find_one({"_id": entry["_id"]})
        utils.make_log("collection", "edit", f"Deleted dataset {ds_uuid}", new_data)

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
    try:
        ds_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)
    dataset = flask.g.db["datasets"].find_one({"_id": ds_uuid})
    if not dataset:
        flask.abort(status=404)
    # permissions
    order = flask.g.db["orders"].find_one({"datasets": ds_uuid})
    if (
        not user.has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in order["editors"]
    ):
        flask.abort(status=403)

    indata = flask.request.json

    validation = utils.basic_check_indata(indata, dataset, prohibited=("_id"))
    if not validation[0]:
        flask.abort(status=validation[1])

    if "description" in indata:
        indata["description"] = utils.secure_description(indata["description"])

    is_different = False
    for field in indata:
        if indata[field] != dataset[field]:
            is_different = True
            break

    if is_different:
        result = flask.g.db["datasets"].update_one(
            {"_id": dataset["_id"]}, {"$set": indata}
        )
        if not result.acknowledged:
            flask.current_app.logger.error("Dataset update failed: %s", dataset)
            flask.abort(status=500)
        else:
            dataset.update(indata)
            utils.make_log("dataset", "edit", "Dataset updated", dataset)

    return flask.Response(status=200)


@blueprint.route("/<identifier>/log", methods=["GET"])
@user.login_required
def get_dataset_log(identifier: str = None):
    """
    Get change logs for the user entry with uuid ``identifier``.

    Can be accessed by creator (order), receiver (order), and admin (DATA_MANAGEMENT).

    Args:
        identifier (str): The uuid of the dataset.

    Returns:
        flask.Response: Logs as json.
    """
    try:
        dataset_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    if not user.has_permission("DATA_MANAGEMENT"):
        order_data = flask.g.db["orders"].find_one({"datasets": dataset_uuid})
        if not order_data:
            flask.abort(403)
        if flask.g.current_user["_id"] not in order_data["editors"]:
            flask.abort(403)

    dataset_logs = list(
        flask.g.db["logs"].find({"data_type": "dataset", "data._id": dataset_uuid})
    )
    for log in dataset_logs:
        del log["data_type"]

    utils.incremental_logs(dataset_logs)

    return utils.response_json(
        {"entry_id": dataset_uuid, "data_type": "dataset", "logs": dataset_logs}
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
    try:
        dataset_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return None
    dataset = flask.g.db["datasets"].find_one({"_id": dataset_uuid})
    if not dataset:
        return None
    order = flask.g.db["orders"].find_one({"datasets": dataset_uuid})

    if (
        user.has_permission("DATA_MANAGEMENT")
        or flask.g.db.current_user["id"] in order["editors"]
    ):
        dataset["order"] = order["_id"]
    dataset["related"] = list(
        flask.g.db["datasets"].find({"_id": {"$in": order["datasets"]}}, {"title": 1})
    )
    dataset["related"].remove({"_id": dataset["_id"], "title": dataset["title"]})
    dataset["collections"] = list(
        flask.g.db["projects"].find({"datasets": dataset_uuid}, {"title": 1})
    )
    for field in ("editors", "generators", "authors"):
        if field == "editors" and (
            not user.has_permission("DATA_MANAGEMENT")
            and flask.g.db.current_user["id"] not in order[field]
        ):
            continue
        dataset[field] = utils.user_uuid_data(order[field], flask.g.db)

    dataset["organisation"] = utils.user_uuid_data(order[field], flask.g.db)
    dataset["organisation"] = (
        dataset["organisation"][0] if dataset["organisation"] else ""
    )
    return dataset
