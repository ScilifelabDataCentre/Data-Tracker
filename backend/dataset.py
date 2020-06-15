"""Dataset requests."""
import json
import logging

import flask

import utils
import user

blueprint = flask.Blueprint('dataset', __name__)  # pylint: disable=invalid-name


@blueprint.route('/', methods=['GET'])
def list_datasets():
    """Provide a simplified list of all available datasets."""
    results = list(flask.g.db['datasets'].find(projection={'title': 1,
                                                           'description': 1,
                                                           '_id': 1}))
    return utils.response_json({'datasets': results})


@blueprint.route('/user/', methods=['GET'])
@user.login_required
def list_user_data():
    """List all datasets belonging to current user."""
    user_orders = list(flask.g.db['orders'].find({'$or': [{'receiver': flask.session['user_id']},
                                                          {'creator': flask.session['user_id']}]},
                                                 {'datasets': 1}))
    uuids = list(ds for entry in user_orders for ds in entry['datasets'])
    user_datasets = list(flask.g.db['datasets'].find({'_id': {'$in': uuids}}))

    return utils.response_json({'datasets': user_datasets})


@blueprint.route('/random/', methods=['GET'])
@blueprint.route('/random/<int:amount>/', methods=['GET'])
def get_random_ds(amount: int = 1):
    """
    Retrieve random dataset(s).

    Args:
        amount (int): number of requested datasets

    Returns:
        flask.Response: json structure for the dataset(s)

    """
    results = list(flask.g.db['datasets'].aggregate([{'$sample': {'size': amount}},
                                                     {'$project': {'_id': 1}}]))
    for i, result in enumerate(results):
        results[i] = build_dataset_info(result['_id'].hex)
    return utils.response_json({'datasets': results})


@blueprint.route('/<identifier>/', methods=['GET'])
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
    return utils.response_json({'dataset': result})


@blueprint.route('/<identifier>/', methods=['DELETE'])
@user.login_required
def delete_dataset(identifier: str):
    """
    Delete a dataset.

    Can be deleted only by creator or user with DATA_MANAGEMENT permissions.

    Args:
        identifier (str): The dataset uuid.
    """
    try:
        ds_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)
    dataset = flask.g.db['datasets'].find_one({'_id': ds_uuid})
    if not dataset:
        flask.abort(status=404)
    # permission check
    order = flask.g.db['orders'].find_one({'datasets': ds_uuid})
    if not user.has_permission('DATA_MANAGEMENT') and \
       order['creator'] != flask.g.current_user['_id']:
        flask.abort(status=403)

    result = flask.g.db['datasets'].delete_one({'_id': ds_uuid})
    if not result.acknowledged:
        logging.error(f'Failed to delete dataset {ds_uuid}')
        return flask.Response(status=500)
    utils.make_log('dataset', 'delete', 'Deleted dataset', data={'_id': ds_uuid})

    for entry in flask.g.db['orders'].find({'datasets': ds_uuid}):
        result = flask.g.db['orders'].update_one({'_id': entry['_id']},
                                                 {'$pull': {'datasets': ds_uuid}})
        if not result.acknowledged:
            logging.error(f'Failed to delete dataset {ds_uuid} in order {entry["_id"]}')
            return flask.Response(status=500)
        new_data = flask.g.db['orders'].find_one({'_id': entry['_id']})
        utils.make_log('order', 'edit', f'Deleted dataset {ds_uuid}', new_data)

    for entry in flask.g.db['projects'].find({'datasets': ds_uuid}):
        flask.g.db['projects'].update_one({'_id': entry['_id']},
                                          {'$pull': {'datasets': ds_uuid}})
        if not result.acknowledged:
            logging.error(f'Failed to delete dataset {ds_uuid} in project {entry["_id"]}')
            return flask.Response(status=500)
        new_data = flask.g.db['projects'].find_one({'_id': entry['_id']})
        utils.make_log('project', 'edit', f'Deleted dataset {ds_uuid}', new_data)

    return flask.Response(status=200)


@blueprint.route('/<identifier>/', methods=['PATCH'])
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
    dataset = flask.g.db['datasets'].find_one({'_id': ds_uuid})
    if not dataset:
        flask.abort(status=404)
    # permissions
    order = flask.g.db['orders'].find_one({'datasets': ds_uuid})
    if not user.has_permission('DATA_MANAGEMENT') and \
       order['creator'] != flask.g.current_user['_id'] and \
       order['receiver'] != flask.g.current_user['_id']:
        flask.abort(status=403)

    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)
    validation = utils.basic_check_indata(indata, dataset, prohibited=('_id'))
    if not validation[0]:
        flask.abort(status=validation[1])
    dataset.update(indata)
    if indata:
        result = flask.g.db['datasets'].update_one({'_id': dataset['_id']}, {'$set': dataset})
        if not result.acknowledged:
            logging.error('Dataset update failed: %s', dataset)
            flask.abort(status=500)
        else:
            utils.make_log('dataset', 'edit', 'Dataset updated', dataset)

    return flask.Response(status=200)


@blueprint.route('/<identifier>/log/', methods=['GET'])
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

    if not user.has_permission('DATA_MANAGEMENT'):
        user_entries = (flask.g.current_user['_id'], flask.g.current_user['email'])
        order_data = flask.g.db['orders'].find_one({'datasets': dataset_uuid})
        if not order_data:
            flask.abort(403)
        if order_data['receiver'] not in user_entries and \
           order_data['creator'] not in user_entries:
           flask.abort(403)

    dataset_logs = list(flask.g.db['logs'].find({'data_type': 'dataset', 'data._id': dataset_uuid}))

    utils.incremental_logs(dataset_logs)

    return utils.response_json({'logs': dataset_logs})


# helper functions
def build_dataset_info(identifier: str):
    """
    Query for a dataset from the database.

    Args:
        identifier (str): The uuid of the dataset.

    Returns:
        dict: The dataset.
    """
    try:
        dataset_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return None
    dataset = flask.g.db['datasets'].find_one({'_id': dataset_uuid})
    if not dataset:
        return None
    order = flask.g.db['orders'].find_one({'datasets': dataset_uuid})
    dataset['related'] = list(flask.g.db['datasets'].find({'_id': {'$in': order['datasets']}},
                                                          {'title': 1}))
    dataset['related'].remove({'_id': dataset['_id'], 'title': dataset['title']})
    dataset['projects'] = list(flask.g.db['projects'].find({'datasets': dataset_uuid},
                                                           {'title': 1}))
    creator = flask.g.db['users'].find_one({'_id': order['creator']})
    if creator:
        dataset['creator'] = creator['name']
    else:
        dataset['creator'] = order['creator']
    return dataset
