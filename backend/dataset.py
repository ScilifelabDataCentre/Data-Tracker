"""Dataset requests."""
import json
import logging
import uuid

import flask

import structure
import utils
import user

blueprint = flask.Blueprint('dataset', __name__)  # pylint: disable=invalid-name


@blueprint.route('/all', methods=['GET'])
def list_datasets():
    """Provide a simplified list of all available datasets."""
    results = list(flask.g.db['datasets'].find(projection={'title': 1,
                                                           'description': 1,
                                                           '_id': 1}))
    return utils.response_json({'datasets': results})


@blueprint.route('/user', methods=['GET'])
@user.login_required
def list_user_data():
    """List all datasets belonging to current user."""
    user_orders = list(flask.g.db['orders'].find({'$or': [{'receiver': flask.session['user_id']},
                                                          {'creator': flask.session['user_id']}]},
                                                 {'datasets': 1}))
    uuids = list(ds for entry in user_orders for ds in entry['datasets'])
    user_datasets = list(flask.g.db['datasets'].find({'_id': {'$in': uuids}},
                                                     {'title': 1}))
    return utils.response_json({'datasets': user_datasets})


@blueprint.route('/random', methods=['GET'])
@blueprint.route('/random/<int:amount>', methods=['GET'])
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


@blueprint.route('/<identifier>', methods=['GET'])
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


@blueprint.route('/<identifier>', methods=['DELETE'])
@user.steward_required
def delete_dataset(identifier):
    """Delete a dataset."""
    try:
        muuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.Response(status=404)

    result = flask.g.db['datasets'].delete_one({'_id': muuid})
    if result.deleted_count == 0:
        return flask.Response(status=404)
    utils.make_log('dataset', 'delete', f'Delete dataset {muuid}')

    for entry in flask.g.db['orders'].find({'datasets': muuid}):
        flask.g.db['orders'].update_one({'_id': entry['_id']},
                                        {'$pull': {'datasets': muuid}})
        new_data = flask.g.db['orders'].find_one({'_id': entry['_id']})
        utils.make_log('order', 'edit', new_data)

    for entry in flask.g.db['projects'].find({'datasets': muuid}):
        flask.g.db['projects'].update_one({'_id': entry['_id']},
                                          {'$pull': {'datasets': muuid}})
        new_data = flask.g.db['projects'].find_one({'_id': entry['_id']})
        utils.make_log('project', 'edit', new_data)

    return flask.Response(status=200)


@blueprint.route('/<identifier>', methods=['PUT'])
@user.steward_or_dsowner_required
# require Steward or owning dataset
def update_dataset(identifier):
    """
    Update a dataset with new values.

    Args:
        identifier (str): uuid for the wanted dataset

    Returns:
        flask.Response: success: 200, failure: 400

    """
    indata = json.loads(flask.request.data)
    try:
        ds_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(flask.Response(status=404))
    if not validate_dataset_input(indata):
        flask.abort(flask.Response(status=400))
    projects = None
    if 'projects' in indata:
        projects = indata['projects']
        del indata['projects']

    if indata:
        response = flask.g.db['datasets'].update_one({'_id': ds_uuid}, {'$set': indata})
        if response.matched_count == 0:
            flask.abort(flask.Response(status=404))
    if projects:
        update_projects(identifier, projects)

    return flask.Response(status=200)


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
    dataset['projects'] = list(flask.g.db['orders'].find({'datasets': dataset_uuid},
                                                         {'title': 1}))
    return dataset
