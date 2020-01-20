"""Dataset requests."""
import json
import logging

import flask

import structure
import utils
import user


blueprint = flask.Blueprint('datasets', __name__)  # pylint: disable=invalid-name

def query_dataset(identifier: str):
    """
    Query for a dataset from the database.

    Args:
        identifier (str): the uuid of the dataset

    Returns:
        dict: the dataset

    """
    try:
        mongo_uuid = utils.to_mongo_uuid(identifier)
        result = flask.g.db['datasets'].find_one({'uuid': mongo_uuid})
        if not result:
            return None
        result['projects'] = list(flask.g.db['projects'].find({'datasets': result['uuid']},
                                                              {'title': 1, 'uuid': 1, '_id': 0}))
        utils.clean_mongo(result)
    except ValueError:
        return None
    return result


def validate_dataset_input(indata):
    """
    Validate the dataset input.

    It may only contain valid fields that may be changed by the role of the current user.

    Args:
        indata: the dataset input

    Returns:
        bool: whether the dataset input is accepted

    """
    # check that fields should exist and are not forbidden
    reference = set(structure.dataset().keys())
    forbidden = {'uuid', 'timestamp', 'identifier'}
    inkeys = set(indata.keys())
    if not inkeys.issubset(reference) or forbidden&inkeys:
        logging.debug('Bad input: %s', inkeys)
        return False

    # check restricted (admin/steward) fields
    restricted_steward = {'creator'}
    if not user.check_user_permissions('Steward') and restricted_steward&inkeys:
        logging.debug('Restricted input: %s', inkeys)
        return False

    return True


@blueprint.route('/all', methods=['GET'])
def list_dataset():
    """Provide a simplified list of all available datasets."""
    results = list(flask.g.db['datasets'].find())
    utils.clean_mongo(results)
    return utils.response_json({'datasets': results})


@blueprint.route('/add', methods=['GET'])
@user.steward_required
def add_dataset_get():
    """Provide a basic data structure for adding a dataset."""
    dataset = structure.dataset()
    del dataset['uuid']
    del dataset['identifier']
    del dataset['timestamp']
    return utils.response_json(dataset)


@blueprint.route('/add', methods=['POST'])
@user.steward_required
def add_dataset_post():
    """Add a dataset."""
    dataset = structure.dataset()
    indata = json.loads(flask.request.data)
    if indata:
        if not validate_dataset_input(indata):
            flask.abort(flask.Response(status=400))
        dataset.update(indata)
    result = flask.g.db['datasets'].insert_one(dataset)
    inserted = flask.g.db['datasets'].find_one({'_id': result.inserted_id})
    return utils.response_json({'uuid': inserted['uuid']})


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
                                                     {'$project': {'_id': 0, 'uuid': 1}}]))
    for i, result in enumerate(results):
        results[i] = query_dataset(result['uuid'].hex)
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
    result = query_dataset(identifier)
    if not result:
        return flask.Response(status=404)
    return utils.response_json({'dataset': result})


@blueprint.route('/<identifier>/delete', methods=['POST'])
@blueprint.route('/<identifier>', methods=['DELETE'])
@user.steward_required
def delete_dataset(identifier):
    """Delete a dataset."""
    try:
        mongo_uuid = utils.to_mongo_uuid(identifier)
    except ValueError:
        return flask.Response(status=404)
    result = flask.g.db['datasets'].delete_one({'uuid': mongo_uuid})
    if result.deleted_count == 0:
        return flask.Response(status=404)
    return flask.Response(status=200)


@blueprint.route('/<identifier>', methods=['PUT'])
@user.login_required
# require Steward or owning dataset
def update_dataset(identifier):
    """
    Update a dataset with new values.

    Args:
        identifier (str): uuid for the wanted dataset

    Returns:
        flask.Response: success: 200, failure: 400

    """
    if not user.check_user_permissions('Steward'):
        current = flask.g.g.db['datasets'].find_one({'uuid': identifier})
        if not utils.is_owner(dataset=current):
            flask.abort(flask.Response(status=403))

    data = flask.request.json
    try:
        utils.check_mongo_update(data)
    except ValueError:
        flask.abort(flask.Response(status=400))
    data['timestamp'] = utils.make_timestamp()
    flask.g.db.datasets.update()
