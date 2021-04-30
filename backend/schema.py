"""Dataset requests."""
import flask

import structure
import utils

blueprint = flask.Blueprint("schema", __name__)  # pylint: disable=invalid-name


@blueprint.route("", methods=["GET"])
def list_available_schemas():
    return utils.response_json({"schemas": ["collection", "dataset", "order", "user"]})


@blueprint.route("/collection", methods=["GET"])
def get_collection_data_structure():
    """
    Get an empty collection entry.

    Returns:
        flask.Response: JSON structure of a collection.
    """
    empty_collection = structure.collection()
    empty_collection["_id"] = ""
    return utils.response_json({"collection": empty_collection})


@blueprint.route("/dataset", methods=["GET"])
def get_dataset_data_structure():
    """
    Get an empty dataset entry.

    Returns:
        flask.Response: JSON structure of a dataset.
    """
    empty_dataset = structure.dataset()
    empty_dataset["_id"] = ""
    return utils.response_json({"dataset": empty_dataset})


@blueprint.route("/order", methods=["GET"])
def get_order_data_structure():
    """
    Get an empty order entry.

    Returns:
        flask.Response: JSON structure of a order.
    """
    empty_order = structure.order()
    empty_order["_id"] = ""
    return utils.response_json({"order": empty_order})


@blueprint.route("/user", methods=["GET"])
def get_user_data_structure():
    """
    Get an empty user entry.

    Returns:
        flask.Response: JSON structure of a user.
    """
    empty_user = structure.user()
    empty_user["_id"] = ""
    return utils.response_json({"user": empty_user})
