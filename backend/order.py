"""
Functions and request handlers related to orders.

Special permissions are required to access orders:

* If you have permission ``DATA_EDIT`` you have CRUD permissions to your own orders.
* If you have permission ``DATA_MANAGEMENT`` you have CRUD permissions to any orders.
"""
import flask

import structure
import user
import utils

blueprint = flask.Blueprint("order", __name__)  # pylint: disable=invalid-name


@blueprint.before_request
def prepare():
    """
    All order request require ``DATA_EDIT``.

    Make sure that the user is logged in and has the required permission.
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)


@blueprint.route("", methods=["GET"])
def list_orders():
    """
    List all orders visible to the current user.

    Returns:
        flask.Response: JSON structure with a list of orders.
    """
    projection = {"_id": 1, "title": 1, "tags": 1, "properties": 1}
    if utils.req_has_permission("DATA_MANAGEMENT"):
        orders = list(flask.g.db["orders"].find(projection=projection))
    else:
        orders = list(
            flask.g.db["orders"].find(
                {"editors": flask.g.current_user["_id"]}, projection=projection
            )
        )

    return utils.response_json({"orders": orders})


@blueprint.route("/<identifier>", methods=["GET"])
def get_order(identifier):
    """
    Retrieve the order with the provided uuid.

    ``order['datasets']`` is returned as ``[{_id, title}, ...]``.

    Args:
        identifier (str): Uuid for the wanted order.

    Returns:
        flask.Response: JSON structure for the order.
    """
    entry = utils.req_get_entry("orders", identifier)
    if not entry:
        flask.abort(status=404)
    if not (
        utils.req_has_permission("DATA_MANAGEMENT")
        or flask.g.current_user["_id"] in entry["editors"]
    ):
        flask.abort(status=403)

    prepare_order_response(entry, flask.g.db)

    return utils.response_json({"order": entry})


@blueprint.route("/<identifier>/log", methods=["GET"])
def get_order_logs(identifier):
    """
    List changes to the dataset.

    Logs will be sorted chronologically.

    The ``data`` in each log will be trimmed to only show the changed fields.

    Args:
        identifier (str): Uuid for the wanted order.

    Returns:
        flask.Response: Json structure for the logs.
    """
    entry = utils.req_get_entry("orders", identifier)
    if not entry:
        flask.abort(status=404)
    if (
        not utils.req_has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in entry["editors"]
    ):
        flask.abort(status=403)

    order_logs = list(
        flask.g.db["logs"].find({"data_type": "order", "data._id": entry["_id"]})
    )
    if not order_logs:
        flask.abort(status=404)

    for log in order_logs:
        del log["data_type"]

    utils.incremental_logs(order_logs)

    return utils.response_json(
        {"entry_id": entry["_id"], "data_type": "order", "logs": order_logs}
    )


@blueprint.route("", methods=["POST"])
def add_order():
    """
    Add an order.

    Returns:
        flask.Response: Json structure with ``_id`` of the added order.
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    # create new order
    new_order = structure.order()

    jsondata = flask.request.json
    if "order" not in jsondata or not isinstance(jsondata["order"], dict):
        flask.abort(status=400)
    indata = jsondata["order"]

    validation = utils.basic_check_indata(indata, new_order, ["_id", "datasets"])
    if not validation.result:
        flask.abort(status=validation.status)

    # add current user to editors if no editors are defined
    if not indata.get("editors"):
        indata["editors"] = [flask.g.current_user["_id"]]
    # add current user if missing and only DATA_EDIT
    elif not utils.req_has_permission("DATA_MANAGEMENT"):
        if flask.g.current_user["_id"] not in indata["editors"]:
            indata["editors"].append(flask.g.current_user["_id"])

    # convert all incoming uuids to uuid.UUID
    for field in ("editors", "authors", "generators"):
        if field in indata:
            indata[field] = [utils.str_to_uuid(entry) for entry in indata[field]]
    if indata.get("organisation"):
        indata["organisation"] = utils.str_to_uuid(indata["organisation"])

    new_order.update(indata)
    new_order["description"] = utils.secure_description(new_order["description"])

    result = utils.req_commit_to_db("orders", "add", new_order)
    if not result.log or not result.data:
        flask.abort(status=500)

    return utils.response_json({"_id": result.ins_id})


@blueprint.route("/<identifier>", methods=["DELETE"])
def delete_order(identifier: str):
    """
    Delete the order with the given identifier.

    Returns:
        flask.Response: Status code
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    entry = utils.req_get_entry("orders", identifier)
    if not entry:
        flask.abort(status=404)

    # permission check
    if (
        not utils.req_has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in entry["editors"]
    ):
        flask.abort(status=403)

    for dataset_uuid in entry["datasets"]:
        result = utils.req_commit_to_db("datasets", "delete", {"_id": dataset_uuid})
        if not result.log or not result.data:
            flask.abort(status=500)
    # delete dataset references in all collections
    collections = list(flask.g.db["collections"].find(
        {"datasets": {"$in": entry["datasets"]}}))
    flask.g.db["collections"].update_many(
        {}, {"$pull": {"datasets": {"$in": entry["datasets"]}}}
    )
    for collection in collections:
        for ds in entry["datasets"]:
            collection["datasets"] = [ds for ds in collection["datasets"] if ds not in entry["datasets"]]
            utils.req_make_log_new(
                data_type="collection",
                action="edit",
                comment="Dataset deleted",
                data=collection,
            )

    result = utils.req_commit_to_db("orders", "delete", {"_id": entry["_id"]})
    if not result.log or not result.data:
        flask.abort(status=500)
    return flask.Response(status=200)


@blueprint.route("/<identifier>", methods=["PATCH"])
def update_order(identifier: str):  # pylint: disable=too-many-branches
    """
    Update an existing order.

    Args:
        identifier (str): Order uuid.

    Returns:
        flask.Response: Status code of the request.
    """
    perm_status = utils.req_check_permissions(["DATA_EDIT"])
    if perm_status != 200:
        flask.abort(status=perm_status)

    order = utils.req_get_entry("orders", identifier)
    if not order:
        flask.abort(status=404)

    # permission check
    if (
        not utils.req_has_permission("DATA_MANAGEMENT")
        and flask.g.current_user["_id"] not in order["editors"]
    ):
        flask.abort(status=403)

    jsondata = flask.request.json
    if "order" not in jsondata or not isinstance(jsondata["order"], dict):
        flask.abort(status=400)
    indata = jsondata["order"]

    validation = utils.basic_check_indata(indata, order, ["_id", "datasets"])
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
    for field in ("editors", "authors", "generators"):
        if field in indata:
            indata[field] = [utils.str_to_uuid(entry) for entry in indata[field]]
    if indata.get("organisation"):
        indata["organisation"] = utils.str_to_uuid(indata["organisation"])

    is_different = False
    for field in indata:
        if indata[field] != order[field]:
            is_different = True
            break

    order.update(indata)
    order["description"] = utils.secure_description(order["description"])

    if indata and is_different:
        result = utils.req_commit_to_db("orders", "edit", order)
        if not result.log or not result.data:
            flask.abort(status=500)

    return flask.Response(status=200)


@blueprint.route("/<identifier>/dataset", methods=["POST"])
def add_dataset(identifier: str):  # pylint: disable=too-many-branches
    """
    Add a dataset to the given order.

    Args:
        identifier (str): The order to add the dataset to.
    """
    # permissions
    indata = flask.request.json
    try:
        order_uuid = utils.str_to_uuid(identifier)
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


def prepare_order_response(order_data: dict, mongodb):
    """
    Prepare an order by e.g. converting user uuids to names etc.

    Changes are done in-place.

    Args:
        order_data (dict): The order entry from the db.
        mongodb: The mongo database to use.
    """
    order_data["authors"] = utils.user_uuid_data(order_data["authors"], mongodb)
    order_data["generators"] = utils.user_uuid_data(order_data["generators"], mongodb)
    order_data["editors"] = utils.user_uuid_data(order_data["editors"], mongodb)
    if order_data["organisation"]:
        if org_entry := utils.user_uuid_data(order_data["organisation"], mongodb):
            order_data["organisation"] = org_entry[0]
        else:
            flask.current_app.logger.error(
                "Reference to non-existing organisation: %s", order_data["organisation"]
            )
    else:
        order_data["organisation"] = {}

    # convert dataset list into {title, _id}
    order_data["datasets"] = list(
        mongodb["datasets"].find(
            {"_id": {"$in": order_data["datasets"]}}, {"_id": 1, "title": 1}
        )
    )
