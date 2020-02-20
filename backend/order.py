"""
Functions and request handlers related to orders.

Special permissions are required to access orders:

* If you have permission ``ORDERS_SELF`` you have CRUD access to your own orders.
* If you have permission ``DATA_MANAGER`` you have CRUD access to any orders.
"""
import flask

import utils
import user


blueprint = flask.Blueprint('orders', __name__)  # pylint: disable=invalid-name

@blueprint.before_request
def prepare():
    """
    All order request require ``ORDERS_SELF``.

    Make sure that the user is logged in and has the required permission.
    """
    import logging
    if not flask.g.current_user:
        flask.abort(status=401)
    if not user.has_permission('ORDERS_SELF'):
        flask.abort(status=403)


@blueprint.route('/user', defaults={'username': None}, methods=['GET'])
@blueprint.route('/user/<user_id>', methods=['GET'])
def list_orders_user(user_id: str):
    """
    List all orders belonging to the provided user.

    Args:
        userid (str): Uuid of user to find orders for.

    Returns:
        flask.Response: Json structure with a list of orders.
    """
    if user_id:
        if not user.has_permission('OWNERS_READ'):
            flask.abort(status=403)
    else:  # current user
        user_id = flask.session['user_id']
    orders = tuple(flask.g.db['orders'].find({'creator': user_id}))

    return utils.response_json({'orders': orders})


@blueprint.route('/<identifier>', methods=['GET'])
def get_order(identifier):
    """
    Retrieve the order with the provided uuid.

    ``order['datasets']`` is returned as ``[{uuid, title}, ...]``.

    Args:
        identifier (str): Uuid for the wanted order.

    Returns:
        flask.Response: Json structure for the order.
    """
    try:
        muuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)
    order = flask.g.db['orders'].find_one({'_id': muuid})
    if not order:
        return flask.abort(status=404)
    if not (user.has_permission('DATA_MANAGEMENT') or
            order['creator'] == flask.session['user_id']):
        return flask.abort(status=403)

    # convert dataset list into {title, uuid}
    for i, ds in enumerate(order['datasets']):
        order['datasets'][i] = next(flask.g.db['datasets']
                                    .aggregate([{'$match': {'_id': ds}},
                                                {'$project': {'_id': 0,
                                                              'uuid': '$_id',
                                                              'title': 1}}]))

    return utils.response_json({'order': order})
