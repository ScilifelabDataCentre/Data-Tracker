"""
Functions and request handlers related to orders.

Special permissions are required to access orders:

* If you have permission ``ORDERS_SELF`` you have CRUD access to your own orders.
* If you have permission ``DATA_MANAGER`` you have CRUD access to any orders.
"""
import logging

import flask

import structure
import user
import utils

blueprint = flask.Blueprint('order', __name__)  # pylint: disable=invalid-name


@blueprint.before_request
def prepare():
    """
    All order request require ``ORDERS_SELF``.

    Make sure that the user is logged in and has the required permission.
    """
    if not flask.g.current_user:
        flask.abort(status=401)
    if not user.has_permission('ORDERS_SELF'):
        flask.abort(status=403)


@blueprint.route('/all', methods=['GET'])
def list_orders():
    """
    List all orders belonging to the provided user.

    Args:
        userid (str): Uuid of user to find orders for.

    Returns:
        flask.Response: Json structure with a list of orders.
    """
    if not user.has_permission('DATA_MANAGEMENT'):
        flask.abort(status=403)
    orders = list(flask.g.db['orders'].find(projection={'_id': 1,
                                                        'title': 1,
                                                        'creator': 1,
                                                        'receiver': 1}))
    return utils.response_json({'orders': orders})


@blueprint.route('/user', defaults={'user_id': None}, methods=['GET'])
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
        try:
            uuid = utils.str_to_uuid(user_id)
        except ValueError:
            return flask.abort(status=404)
    else:  # current user
        uuid = flask.session['user_id']
    orders = list(flask.g.db['orders'].find({'$or': [{'receiver': uuid},
                                                     {'creator': uuid}]}))
    if not orders:
        flask.abort(status=404)

    return utils.response_json({'orders': orders})


@blueprint.route('/<identifier>', methods=['GET'])
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
        return flask.abort(status=404)
    order = flask.g.db['orders'].find_one({'_id': uuid})
    if not order:
        return flask.abort(status=404)
    if not (user.has_permission('DATA_MANAGEMENT') or
            order['creator'] == flask.session['user_id']):
        return flask.abort(status=403)

    # convert dataset list into {title, _id}
    order['datasets'] = list(flask.g.db['datasets']
                             .find({'_id': {'$in': order['datasets']}},
                                   {'_id': 1,
                                    'title': 1}))

    return utils.response_json({'order': order})


@blueprint.route('/<identifier>/log', methods=['GET'])
def get_order_log(identifier):
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
        uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)

    order = flask.g.db['orders'].find_one({'_id': uuid})
    if order:
        is_owner = order['creator'] == flask.session['user_id']
    logs = list(flask.g.db['logs'].find({'data_type': 'order', 'data._id': uuid}))
    if not (user.has_permission('DATA_MANAGEMENT') or is_owner):
        return flask.abort(status=403)
    if not logs:
        return flask.abort(status=404)

    utils.incremental_logs(logs)

    return utils.response_json({'logs': logs})


@blueprint.route('/<_>/addDataset', methods=['GET'])
@user.login_required
def add_dataset_get(_):
    """
    Provide a basic data structure for adding a dataset.

    The structure will be returned no matter what "uuid" it is provided.
    """
    dataset = structure.dataset()
    del dataset['_id']
    return utils.response_json(dataset)


@blueprint.route('/<identifier>/addDataset', methods=['POST'])
@user.login_required
def add_dataset_post(identifier):  # pylint: disable=too-many-branches
    """Add a dataset."""
    # permissions
    if not user.has_permission('ORDERS_SELF'):
        flask.abort(status=403)
    try:
        muuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)
    order = flask.g.db['orders'].find_one({'_id': muuid})
    if not order:
        flask.abort(status=404)
    if not (user.has_permission('DATA_MANAGEMENT') or
            order['creator'] == flask.session['user_id']):
        return flask.abort(status=403)

    # create new dataset
    dataset = structure.dataset()
    indata = flask.json.loads(flask.request.data)

    # indata validation
    if '_id' in indata:
        flask.abort(status=400)
    for key in indata:
        if key not in dataset:
            flask.abort(status=400)
        if not utils.validate_infield(key, indata[key]):
            logging.debug(f'Key: {key}, Data: {indata[key]}')
            flask.abort(status=400)
    dataset.update(indata)

    # add to db
    result_ds = flask.g.db['datasets'].insert_one(dataset)
    if not result_ds.acknowledged:
        logging.error('Dataset insert failed: %s', dataset)
    else:
        utils.make_log('dataset',
                       'add',
                       f'Dataset added for order {muuid}',
                       dataset)

        result_o = flask.g.db['orders'].update_one({'_id': muuid},
                                                   {'$push': {'datasets': dataset['_id']}})
        if not result_o.acknowledged:
            logging.error('Order insert failed: ADD dataset %s', dataset['_id'])
        else:
            order = flask.g.db['orders'].find_one({'_id': muuid})

            utils.make_log('order',
                           'update',
                           f'Dataset {result_ds.inserted_id} added for order',
                           order)

    return utils.response_json({'_id': result_ds.inserted_id})
