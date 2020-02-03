"""Order requests."""
import json
import logging
import uuid

import flask

import structure
import utils
import user


blueprint = flask.Blueprint('orders', __name__)  # pylint: disable=invalid-name


@blueprint.route('/user', methods=['GET'])
@user.login_required
def list_orders_self():
    """List all orders belonging to current user."""
    user_orders = tuple(flask.g.db['orders'].find({'$or': [{'receiver': flask.session['username']},
                                                           {'creator': flask.session['username']}]}))

    return utils.response_json({'orders': user_orders})


@blueprint.route('/user/<username>', methods=['GET'])
@user.steward_required
def list_orders_user(username: str):
    """
    List all orders belonging to the provided user.

    Args:
        username (str): username to find orders for

    """
    user_orders = tuple(flask.g.db['orders'].find({'$or': [{'receiver': username},
                                                           {'creator': username}]}))

    return utils.response_json({'orders': user_orders})


@blueprint.route('/add', methods=['GET'])
@user.steward_required
def add_order_get():
    """Provide a basic data structure for adding a order."""
    order = structure.order()
    del order['uuid']
    del order['identifier']
    del order['timestamp']
    order['projects'] = []
    return utils.response_json(order)


@blueprint.route('/add', methods=['POST'])
@user.steward_required
def add_order_post():
    """Add a order."""
    order = structure.order()

    indata = json.loads(flask.request.data)
    if indata:
        if not validate_order_input(indata):
            flask.abort(flask.Response(status=400))
        order.update(indata)

    identifier = order['uuid'].hex()
    identifier = (f'{identifier[:8]}-{identifier[8:12]}-' +
                  f'{identifier[12:16]}-{identifier[16:20]}-{identifier[20:]}')
    if 'projects' in order:
        update_projects(identifier, order['projects'])
        del order['projects']

    result = flask.g.db['orders'].insert_one(order)
    entry = flask.g.db['orders'].find_one({'_id': result.inserted_id},
                                            {'uuid': 1, '_id': 0})
    return utils.response_json(entry)


@blueprint.route('/<identifier>', methods=['GET'])
def get_order(identifier):
    """
    Retrieve the order with the provided uuid.

    Args:
        identifier (str): uuid for the wanted order

    Returns:
        flask.Response: json structure for the order

    """
    result = flask.g.db['orders'].find_one({'_id': utils.str_to_mongo_uuid(identifier)})
    logging.error(result)
    if not result:
        return flask.Response(status=404)
    return utils.response_json({'order': result})
