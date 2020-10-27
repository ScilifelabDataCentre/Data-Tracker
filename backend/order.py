"""
Functions and request handlers related to orders.

Special permissions are required to access orders:

* If you have permission ``ORDERS`` you have CRUD access to your own orders.
* If you have permission ``DATA_MANAGER`` you have CRUD access to any orders.
"""
import json

import flask

import structure
import user
import utils

blueprint = flask.Blueprint('order', __name__)  # pylint: disable=invalid-name


@blueprint.before_request
def prepare():
    """
    All order request require ``ORDERS``.

    Make sure that the user is logged in and has the required permission.
    """
    if not flask.g.current_user:
        flask.abort(status=401)
    if not user.has_permission('ORDERS'):
        flask.abort(status=403)


@blueprint.route('/', methods=['GET'])
def list_orders():
    """
    List all orders visible to the current user.

    Returns:
        flask.Response: JSON structure with a list of orders.
    """
    if user.has_permission('DATA_MANAGEMENT'):
        orders = list(flask.g.db['orders'].find(projection={'_id': 1,
                                                            'title': 1}))
    else:
        orders = list(flask.g.db['orders']
                      .find({'editors': flask.g.current_user['_id']},
                            projection={'_id': 1,
                                        'title': 1}))

    return utils.response_json({'orders': orders})


@blueprint.route('/structure/', methods=['GET'])
def get_order_data_structure():
    """
    Get an empty order entry.

    Returns:
        flask.Response: JSON structure with a list of orders.
    """
    empty_order = structure.order()
    empty_order['_id'] = ''
    return utils.response_json({'order': empty_order})


@blueprint.route('/user/', defaults={'user_id': None}, methods=['GET'])
@blueprint.route('/user/<user_id>/', methods=['GET'])
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
        try:
            user_uuid = utils.str_to_uuid(user_id)
        except ValueError:
            return flask.abort(status=404)
        if not flask.g.db['users'].find_one({'_id': user_uuid}):
            return flask.abort(status=404)
    else:  # current user
        user_uuid = flask.session['user_id']
    orders = list(flask.g.db['orders'].find({'editors': user_uuid},
                                            projection={'_id': 1,
                                                        'title': 1}))

    return utils.response_json({'orders': orders})


@blueprint.route('/<identifier>/', methods=['GET'])
def get_order(identifier):
    """
    Retrieve the order with the provided uuid.

    ``order['datasets']`` is returned as ``[{_id, title}, ...]``.

    Args:
        identifier (str): Uuid for the wanted order.

    Returns:
        flask.Response: Json structure for the order.
    """
    try:
        uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)
    order_data = flask.g.db['orders'].find_one({'_id': uuid})
    if not order_data:
        flask.abort(status=404)
    if not (user.has_permission('DATA_MANAGEMENT') or
            flask.session['user_id'] in order_data['editors']):
        flask.abort(status=403)

    prepare_order_response(order_data, flask.g.db)

    return utils.response_json({'order': order_data})


@blueprint.route('/<identifier>/log/', methods=['GET'])
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
    try:
        order_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    if not user.has_permission('DATA_MANAGEMENT'):
        order_data = flask.g.db['orders'].find_one({'_id': order_uuid})
        if not order_data or flask.g.current_user['_id'] not in order_data['editors']:
            flask.abort(403)

    order_logs = list(flask.g.db['logs'].find({'data_type': 'order', 'data._id': order_uuid}))
    for log in order_logs:
        del log['data_type']

    utils.incremental_logs(order_logs)

    return utils.response_json({'entry_id': order_uuid,
                                'data_type': 'order',
                                'logs': order_logs})


@blueprint.route('/base/', methods=['GET'])
def get_empty_order():
    """
    Provide the basic data structure for an empty order.

    Returns:
        flask.Response: Json structure of an empty order.
    """
    # create new order
    order = structure.order()
    order['_id'] = ''

    return utils.response_json({'order': order})


@blueprint.route('/', methods=['POST'])
def add_order():
    """
    Add an order.

    Returns:
        flask.Response: Json structure with ``_id`` of the added order.
    """
    # create new order
    new_order = structure.order()
    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.current_app.logger.debug('Bad json')
        flask.abort(status=400)

    validation = utils.basic_check_indata(indata, new_order, ['_id', 'datasets'])
    if not validation.result:
        flask.abort(status=validation.status)

    for field in ('editors', 'authors', 'generators'):
        if field in indata:
            indata[field] = [utils.str_to_uuid(entry) for entry in indata[field]]
    if 'organisation' in indata:
        if indata['organisation']:
            indata['organisation'] = utils.str_to_uuid(indata['organisation'])

    new_order.update(indata)

    if flask.g.current_user['_id'] not in new_order['editors']:
        new_order['editors'].append(flask.g.current_user['_id'])

    # add to db
    result = flask.g.db['orders'].insert_one(new_order)
    if not result.acknowledged:
        flask.current_app.logger.error('Order insert failed: %s', new_order)
    else:
        utils.make_log('order', 'add', 'Order added', new_order)

    return utils.response_json({'_id': result.inserted_id})


@blueprint.route('/<identifier>/', methods=['DELETE'])
def delete_order(identifier: str):
    """
    Delete the order with the given identifier.

    Returns:
        flask.Response: Status code
    """
    try:
        order_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)
    order = flask.g.db['orders'].find_one({'_id': order_uuid})
    if not order:
        flask.abort(status=404)
    if not user.has_permission('DATA_MANAGEMENT') and \
       flask.g.current_user['_id'] not in order['editors']:
        flask.abort(status=403)

    for dataset_uuid in order['datasets']:
        result = flask.g.db['datasets'].delete_one({'_id': dataset_uuid})
        if not result.acknowledged:
            flask.current_app.logger.error('Dataset %s delete failed (order %s deletion):',
                          dataset_uuid, order_uuid)
            flask.abort(status=500)
        else:
            utils.make_log('dataset', 'delete', 'Deleting order', {'_id': dataset_uuid})
    result = flask.g.db['orders'].delete_one(order)
    if not result.acknowledged:
        flask.current_app.logger.error('Order deletion failed: %s', order_uuid)
        flask.abort(status=500)
    else:
        utils.make_log('order', 'delete', 'Order deleted', {'_id': order_uuid})

    return flask.Response(status=200)


@blueprint.route('/<identifier>/', methods=['PATCH'])
def update_order(identifier: str):  # pylint: disable=too-many-branches
    """
    Update an existing order.

    Args:
        identifier (str): Order uuid.

    Returns:
        flask.Response: Status code of the request.
    """
    try:
        order_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)

    order = flask.g.db['orders'].find_one({'_id': order_uuid})
    if not order:
        return flask.abort(status=404)
    if not (user.has_permission('DATA_MANAGEMENT') or
            flask.g.current_user['_id'] in order['editors']):
        return flask.abort(status=403)

    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)
    validation = utils.basic_check_indata(indata, order, ['_id', 'datasets'])
    if not validation.result:
        flask.abort(status=validation.status)

    for field in ('editors', 'authors', 'generators'):
        if field in indata:
            indata[field] = [utils.str_to_uuid(entry) for entry in indata[field]]
    if 'organisation' in indata:
        if indata['organisation']:
            indata['organisation'] = utils.str_to_uuid(indata['organisation'])

    is_different = False
    for field in indata:
        if indata[field] != order[field]:
            is_different = True
            break

    order.update(indata)

    if is_different:
        result = flask.g.db['orders'].update_one({'_id': order['_id']}, {'$set': order})
        if not result.acknowledged:
            flask.current_app.logger.error('Order update failed: %s', order)
        else:
            utils.make_log('order', 'edit', 'Order updated', order)

    return flask.Response(status=200)


def prepare_order_response(order_data: dict, mongodb):
    """
    Prepare an order by e.g. converting user uuids to names etc.

    Changes are done in-place.

    Args:
        order_data (dict): The order entry from the db.
        mongodb: The mongo database to use.
    """
    order_data['authors'] = utils.user_uuid_data(order_data['authors'], mongodb)
    order_data['generators'] = utils.user_uuid_data(order_data['generators'], mongodb)
    order_data['editors'] = utils.user_uuid_data(order_data['editors'], mongodb)
    if order_data['organisation']:
        if org_entry := utils.user_uuid_data(order_data['organisation'], mongodb):
            order_data['organisation'] = org_entry[0]
        else:
            flask.current_app.logger.error('Reference to non-existing organisation: %s',
                                           order_data['organisation'])
    else:
        order_data['organisation'] = {}

    # convert dataset list into {title, _id}
    order_data['datasets'] = list(mongodb['datasets'].find({'_id': {'$in': order_data['datasets']}},
                                                           {'_id': 1, 'title': 1}))
