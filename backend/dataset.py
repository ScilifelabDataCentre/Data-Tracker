"""Dataset requests."""
import json

import flask

import structure
import utils
import user

blueprint = flask.Blueprint("dataset", __name__)  # pylint: disable=invalid-name


@blueprint.route("/", methods=["GET"])
def list_datasets():
    """Provide a simplified list of all available datasets."""
    results = list(
        flask.g.db["datasets"].find(
            projection={"title": 1, "_id": 1, "tags": 1, "properties": 1}
        )
    )
    return utils.response_json({"datasets": results})


@blueprint.route("/user/", methods=["GET"])
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


@blueprint.route("/random/", methods=["GET"])
@blueprint.route("/random/<int:amount>/", methods=["GET"])
def get_random_ds(amount: int = 1):
    """
    Retrieve random dataset(s).

    Args:
        amount (int): number of requested datasets

    Returns:
        flask.Response: json structure for the dataset(s)

    """
    results = list(
        flask.g.db["datasets"].aggregate(
            [{"$sample": {"size": amount}}, {"$project": {"_id": 1}}]
        )
    )
    for i, result in enumerate(results):
        results[i] = build_dataset_info(result["_id"].hex)
    return utils.response_json({"datasets": results})


@blueprint.route("/structure/", methods=["GET"])
def get_dataset_data_structure():
    """
    Get an empty dataset entry.

    Returns:
        flask.Response: JSON structure with a list of datasets.
    """
    empty_dataset = structure.dataset()
    empty_dataset["_id"] = ""
    return utils.response_json({"dataset": empty_dataset})


@blueprint.route("/<identifier>/", methods=["GET"])
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


@blueprint.route("/", methods=["POST"])
@user.login_required
def add_dataset():  # pylint: disable=too-many-branches
    """
    Add a dataset to the given order.

    Args:
        identifier (str): The order to add the dataset to.
    """
    # permissions
    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)
    if not "order" in indata:
        flask.current_app.logger.debug("Order field missing")
        flask.abort(status=400)
    try:
        order_uuid = utils.str_to_uuid(indata["order"])
    except ValueError:
        flask.current_app.logger.debug("Incorrect order UUID (%s)", indata["order"])
        flask.abort(status=400)
    order = flask.g.db["orders"].find_one({"_id": order_uuid})
    if not order:
        flask.current_app.logger.debug("Order (%s) not in db", indata["order"])
        flask.abort(status=400)
    if not (
        user.has_permission("DATA_MANAGEMENT")
        or flask.g.current_user["_id"] in order["editors"]
    ):
        return flask.abort(status=403)
    del indata["order"]

    # properties may only be set by users with DATA_MANAGEMENT
    if "properties" in indata:
        if not user.has_permission("DATA_MANAGEMENT"):
            flask.abort(403)

    # create new dataset
    dataset = structure.dataset()
    validation = utils.basic_check_indata(indata, dataset, ["_id"])
    if not validation.result:
        flask.abort(status=validation.status)
    dataset.update(indata)

    dataset["description"] = utils.secure_description(dataset["description"])

    # add to db
    result_ds = flask.g.db["datasets"].insert_one(dataset)
    if not result_ds.acknowledged:
        flask.current_app.logger.error("Dataset insert failed: %s", dataset)
    else:
        utils.make_log(
            "dataset", "add", f"Dataset added for order {order_uuid}", dataset
        )

        result_o = flask.g.db["orders"].update_one(
            {"_id": order_uuid}, {"$push": {"datasets": dataset["_id"]}}
        )
        if not result_o.acknowledged:
            flask.current_app.logger.error(
                "Order %s insert failed: ADD dataset %s", order_uuid, dataset["_id"]
            )
        else:
            order = flask.g.db["orders"].find_one({"_id": order_uuid})

            utils.make_log(
                "order",
                "edit",
                f"Dataset {result_ds.inserted_id} added for order",
                order,
            )

    return utils.response_json({"_id": result_ds.inserted_id})


@blueprint.route("/<identifier>/", methods=["DELETE"])
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


@blueprint.route("/<identifier>/", methods=["PATCH"])
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

    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)
    validation = utils.basic_check_indata(indata, dataset, prohibited=("_id"))
    if not validation[0]:
        flask.abort(status=validation[1])

    # properties may only be set by users with DATA_MANAGEMENT
    if "properties" in indata:
        if not user.has_permission("DATA_MANAGEMENT"):
            flask.abort(403)

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


@blueprint.route("/<identifier>/log/", methods=["GET"])
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
