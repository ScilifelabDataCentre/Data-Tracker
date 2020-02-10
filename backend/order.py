"""Order requests."""
import flask

import utils
import user


blueprint = flask.Blueprint('orders', __name__)  # pylint: disable=invalid-name


@blueprint.route('/user', defaults={'username': None}, methods=['GET'])
@blueprint.route('/user/<username>', methods=['GET'])
@user.steward_required
def list_orders_user(username: str):
    """
    List all orders belonging to the provided user.

    Args:
        username (str): username to find orders for

    """
    if not username:
        username = flask.session['username']
    orders = tuple(flask.g.db['orders'].find({'$or': [{'receiver': username},
                                                      {'creator': username}]}))

    return utils.response_json({'orders': orders})


@blueprint.route('/<identifier>', methods=['GET'])
def get_order(identifier):
    """
    Retrieve the order with the provided uuid.

    Args:
        identifier (str): uuid for the wanted order

    Returns:
        flask.Response: json structure for the order

    """
    try:
        muuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)
    result = flask.g.db['orders'].find_one({'_id': muuid})
    if not result:
        return flask.abort(status=404)
    return utils.response_json({'order': result})
