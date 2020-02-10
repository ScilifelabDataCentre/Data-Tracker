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
    if not utils.check_mongo_update(indata):
        return False
    # check that fields should exist and are not forbidden
    reference = set(structure.dataset().keys())
    reference.add('projects')
    forbidden = {'_id', 'identifiers'}
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
    ds_uuid = utils.str_to_mongo_uuid(dataset_uuid)
    old_projects = {item['_id']
                    for item in
                    flask.g.db['projects'].find({'datasets': ds_uuid},
                                                {'_id': 1})}
    new_projects = {uuid.UUID(proj) for proj in in_projects}
    to_remove = old_projects-new_projects
    to_add = new_projects-old_projects
    for proj in to_remove:
        response = (flask.g.db['projects']
                    .update({'_id': utils.uuid_to_mongo_uuid(proj)},
                            {'$pull': {'datasets': ds_uuid}}))
        if not response['nModified']:
            logging.error('Dataset %s not listed in project %s',
                          dataset_uuid, proj)
    for proj in to_add:
        response = (flask.g.db['projects']
                    .update({'_id': utils.uuid_to_mongo_uuid(proj)},
                            {'$push': {'datasets': ds_uuid}}))
        if not response['nModified']:
            logging.error('Dataset %s not listed in project %s',
                          dataset_uuid, proj)


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
    user_projects = tuple(flask.g.db['orders']
                          .find({'$or': [{'receiver': flask.session['username']},
                                         {'creator': flask.session['username']}]},
                                {'datasets': 1}))
    uuids = tuple(utils.uuid_to_mongo_uuid(ds)
                  for entry in user_projects for ds in entry['datasets'])
    user_datasets = list(flask.g.db['datasets'].find({'uuid': {'$in': uuids}},
                                                     {'title': 1}))
    logging.error(user_datasets)
    return utils.response_json({'datasets': user_datasets})


@blueprint.route('/add', methods=['GET'])
@user.steward_required
def add_dataset_get():
    """Provide a basic data structure for adding a dataset."""
    dataset = structure.dataset()
    logging.error(dataset)
    del dataset['_id']
    del dataset['identifiers']
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

    identifier = dataset['_id'].hex()
    identifier = (f'{identifier[:8]}-{identifier[8:12]}-' +
                  f'{identifier[12:16]}-{identifier[16:20]}-{identifier[20:]}')
    if 'projects' in dataset:
        update_projects(identifier, dataset['projects'])
        del dataset['projects']

    result = flask.g.db['datasets'].insert_one(dataset)
    entry = flask.g.db['datasets'].find_one({'_id': result.inserted_id},
                                            {'_id': 1})
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
                                                     {'$project': {'_id': 1}}]))
    for i, result in enumerate(results):
        results[i] = utils.get_dataset(result['_id'].hex)
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
        mongo_uuid = utils.str_to_mongo_uuid(identifier)
    except ValueError:
        return flask.Response(status=404)

    result = flask.g.db['datasets'].delete_one({'_id': mongo_uuid})
    if result.deleted_count == 0:
        return flask.Response(status=404)
    utils.make_log('dataset', 'delete')

    for entry in flask.g.db['orders'].find({'datasets': mongo_uuid}):
        logging.error(f'flaff: {entry}')
        flask.g.db['orders'].update_one({'_id': utils.uuid_to_mongo_uuid(entry['_id'])},
                                        {'$pull': {'datasets': mongo_uuid}})
        new_data = flask.g.db['orders'].find_one({'_id': utils.uuid_to_mongo_uuid(entry['_id'])})
        new_data['_id'] = utils.uuid_to_mongo_uuid(new_data['_id'])
        utils.make_log('order', 'edit', new_data)

    for entry in flask.g.db['projects'].find({'datasets': mongo_uuid}):
        flask.g.db['projects'].update_one({'_id': utils.uuid_to_mongo_uuid(entry['_id'])},
                                          {'$pull': {'datasets': mongo_uuid}})
        new_data = flask.g.db['projects'].find_one({'_id': utils.uuid_to_mongo_uuid(entry['_id'])})
        new_data['_id'] = utils.uuid_to_mongo_uuid(new_data['_id'])
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
        ds_uuid = utils.str_to_mongo_uuid(identifier)
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
