"""Dataset requests."""
import json
import logging
import uuid

import flask

import structure
import utils
import user


blueprint = flask.Blueprint('datasets', __name__)  # pylint: disable=invalid-name


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
    reference.add('projects')
    forbidden = {'uuid', 'timestamp', 'identifier'}
    inkeys = set(indata.keys())
    if not inkeys.issubset(reference) or forbidden&inkeys:
        logging.debug('Bad input: %s', inkeys)
        return False

    # check restricted (admin/steward) fields
    restricted_steward = {'creator', 'projects'}
    if not user.check_user_permissions('Steward') and restricted_steward&inkeys:
        logging.debug('Restricted input: %s', inkeys)
        return False

    return True


def update_projects(dataset_uuid: str, in_projects: list):
    """
    Update the dataset list in the projects the dataset is connected to.

    Remove the dataset from projects in old_projects that are not in new_projects,
    and add the dataset to the new projects.

    Args:
        dataset_uuid (str): the uuid of the dataset
        new_projects (list): the project uuids (str) the dataset should now be related to

    Raises:
        ValueError: a project uuid did not match any project in the db

    """
    ds_uuid = utils.to_mongo_uuid(dataset_uuid)
    old_projects = {item['uuid']
                    for item in
                    flask.g.db['projects'].find({'datasets': ds_uuid},
                                                {'uuid': 1, '_id': 0})}
    new_projects = {uuid.UUID(proj) for proj in in_projects}
    to_remove = old_projects-new_projects
    to_add = new_projects-old_projects
    for proj in to_remove:
        response = (flask.g.db['projects']
                    .update({'uuid': utils.uuid_convert_mongo(proj)},
                            {'$pull': {'datasets': ds_uuid}}))
        if not response['nModified']:
            logging.error('Dataset %s not listed in project %s',
                          dataset_uuid, proj)
    for proj in to_add:
        response = (flask.g.db['projects']
                    .update({'uuid': utils.uuid_convert_mongo(proj)},
                            {'$push': {'datasets': ds_uuid}}))
        if not response['nModified']:
            logging.error('Dataset %s not listed in project %s',
                          dataset_uuid, proj)


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
    dataset['projects'] = []
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

    identifier = dataset['uuid'].hex()
    identifier = (f'{identifier[:8]}-{identifier[8:12]}-' +
                  f'{identifier[12:16]}-{identifier[16:20]}-{identifier[20:]}')
    if 'projects' in dataset:
        update_projects(identifier, dataset['projects'])
        del dataset['projects']

    result = flask.g.db['datasets'].insert_one(dataset)
    entry = flask.g.db['datasets'].find_one({'_id': result.inserted_id},
                                            {'uuid': 1, '_id': 0})
    return utils.response_json(entry)


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
        results[i] = utils.get_dataset(result['uuid'].hex)
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
    result = utils.get_dataset(identifier)
    if not result:
        return flask.Response(status=404)
    return utils.response_json({'dataset': result})


@blueprint.route('/<identifier>/delete', methods=['POST'])  # post to make sure csrf is used
@blueprint.route('/<identifier>', methods=['DELETE'])
@user.steward_required
def delete_dataset(identifier):
    """Delete a dataset."""
    try:
        mongo_uuid = utils.to_mongo_uuid(identifier)
    except ValueError:
        return flask.Response(status=404)
    logging.error(list(flask.g.db['projects'].find({'datasets': mongo_uuid})))

    response = (flask.g.db['projects'].update_many({'datasets': mongo_uuid},
                                                   {'$pull': {'datasets': mongo_uuid}}))
    logging.error(response.matched_count)
    logging.error(response.modified_count)

    result = flask.g.db['datasets'].delete_one({'uuid': mongo_uuid})
    if result.deleted_count == 0:
        return flask.Response(status=404)
    return flask.Response(status=200)


@blueprint.route('/<identifier>', methods=['PUT'])
@blueprint.route('/<identifier>/edit', methods=['POST'])
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
    data = json.loads(flask.request.data)
    try:
        utils.check_mongo_update(data)
    except ValueError:
        flask.abort(flask.Response(status=400))
    if 'projects' in data:
        if not user.check_user_permissions('Steward'):
            flask.abort(flask.Response(status=401))
        update_projects(identifier, data['projects'])
        del data['projects']
    data['timestamp'] = utils.make_timestamp()
    flask.g.db.datasets.update({'uuid': identifier}, data)
