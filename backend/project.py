"""Project requests."""
import json
import logging

import flask

import structure
import user
import utils

blueprint = flask.Blueprint('project', __name__)  # pylint: disable=invalid-name


@blueprint.route('/', methods=['GET'])
def list_project():
    """Provide a simplified list of all available projects."""
    results = list(flask.g.db['projects'].find())
    return utils.response_json({'projects': results})


@blueprint.route('/random/', methods=['GET'])
@blueprint.route('/random/<int:amount>', methods=['GET'])
def get_random(amount: int = 1):
    """
    Retrieve random project(s).

    Args:
        amount (int): number of requested projects

    Returns:
        flask.Request: json structure for the project(s)

    """
    results = list(flask.g.db['projects'].aggregate([{'$sample': {'size': amount}}]))

    for result in results:
        # only show owner if owner/admin
        if not flask.g.current_user or\
           (not user.has_permission('DATA_MANAGEMENT') and
            flask.g.current_user['_id'] not in result['owners'] and
            flask.g.current_user['email'] not in result['owners']):
            logging.debug('Not allowed to access owners %s', flask.g.current_user)
            del result['owners']

            # return {_id, _title} for datasets
            result['datasets'] = [flask.g.db.datasets.find_one({'_id': dataset},
                                                               {'title': 1})
                                  for dataset in result['datasets']]
    return utils.response_json({'projects': results})


@blueprint.route('/<identifier>/', methods=['GET'])
def get_project(identifier):
    """
    Retrieve the project with uuid <identifier>.

    Args:
        identifier (str): uuid for the wanted project

    Returns:
        flask.Request: json structure for the project

    """
    try:
        uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    result = flask.g.db['projects'].find_one({'_id': uuid})
    if not result:
        return flask.Response(status=404)

    # only show owner if owner/admin
    if not flask.g.current_user or\
       (not user.has_permission('DATA_MANAGEMENT') and
        flask.g.current_user['_id'] not in result['owners'] and
        flask.g.current_user['email'] not in result['owners']):
        logging.debug('Not allowed to access owners %s', flask.g.current_user)
        del result['owners']
    else:
        for i, owner in enumerate(result['owners']):
            if not utils.is_email(owner):
                owner_info = flask.g.db['users'].find_one(owner)
                result['owners'][i] = owner_info['email']

    # return {_id, _title} for datasets
    result['datasets'] = [flask.g.db.datasets.find_one({'_id': dataset},
                                                       {'title': 1})
                          for dataset in result['datasets']]

    return utils.response_json({'project': result})


@blueprint.route('/', methods=['POST'])
@user.login_required
def add_project():  # pylint: disable=too-many-branches
    """
    Add a project.

    Returns:
        flask.Response: Json structure with the ``_id`` of the project.
    """
    # create new project
    project = structure.project()

    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)

    # indata validation
    validation = utils.basic_check_indata(indata, project, prohibited=('_id'))
    if not validation[0]:
        flask.abort(status=validation[1])

    if 'title' not in indata:
        flask.abort(status=400)

    if not indata.get('owners'):
        indata['owners'] = [flask.g.current_user['_id']]
    else:
        for i, owner in enumerate(indata['owners']):
            if utils.is_email(owner):
                owner_info = flask.g.db['users'].find_one({'email': owner})
                if owner_info:
                    indata['owners'][i] = owner_info['_id']

    if 'datasets' in indata:
        for i, dataset_uuid_str in enumerate(indata['datasets']):
            dataset_uuid = utils.str_to_uuid(dataset_uuid_str)
            indata['datasets'][i] = dataset_uuid
            # allow new ones only if owner or DATA_MANAGEMENT
            order_info = flask.g.db['orders'].find_one({'datasets': dataset_uuid})
            if not order_info:
                flask.abort(status=400)
            if not user.has_permission('DATA_MANAGEMENT') and\
               order_info['creator'] != flask.g.current_user['_id'] and\
               order_info['receiver'] != flask.g.current_user['_id']:
                flask.abort(status=400)

    project.update(indata)

    # add to db
    result = flask.g.db['projects'].insert_one(project)
    if not result.acknowledged:
        logging.error('Project insert failed: %s', project)
    else:
        utils.make_log('project', 'add', 'Project added', project)

    return utils.response_json({'_id': result.inserted_id})


@blueprint.route('/<identifier>/', methods=['DELETE'])
@user.login_required
def delete_project(identifier: str):
    """
    Delete a project.

    Can be deleted only by an owner or user with DATA_MANAGEMENT permissions.

    Args:
        identifier (str): The project uuid.
    """
    try:
        ds_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)
    project = flask.g.db['projects'].find_one({'_id': ds_uuid})
    if not project:
        flask.abort(status=404)

    # permission check
    if not user.has_permission('DATA_MANAGEMENT'):
        if flask.g.current_user['_id'] not in project['owners']:
            flask.abort(status=403)

    result = flask.g.db['projects'].delete_one({'_id': ds_uuid})
    if not result.acknowledged:
        logging.error(f'Failed to delete project {ds_uuid}')
        return flask.Response(status=500)
    utils.make_log('project', 'delete', 'Deleted project', data={'_id': ds_uuid})

    return flask.Response(status=200)


@blueprint.route('/<identifier>/', methods=['PATCH'])
@user.login_required
def update_project(identifier):  # pylint: disable=too-many-branches
    """
    Update a project.

    Args:
        identifier (str): The project uuid.

    Returns:
        flask.Response: Status code.
    """
    try:
        project_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        return flask.abort(status=404)
    project = flask.g.db['projects'].find_one({'_id': project_uuid})
    if not project:
        flask.abort(status=404)

    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)

    # permission check
    if not user.has_permission('DATA_MANAGEMENT'):
        if flask.g.current_user['_id'] not in project['owners'] and\
           flask.g.current_user['email'] not in project['owners']:
            logging.debug('Unauthorized update attempt (project %s, user %s)',
                          project_uuid,
                          flask.g.current_user['_id'])
            flask.abort(status=403)

    # indata validation
    validation = utils.basic_check_indata(indata, project, prohibited=('_id'))
    if not validation[0]:
        flask.abort(status=validation[1])

    if indata.get('owners'):
        for i, owner in enumerate(indata['owners']):
            if utils.is_email(owner):
                owner_info = flask.g.db['users'].find_one({'email': owner})
                if owner_info:
                    indata['owners'][i] = owner_info['_id']

    if 'datasets' in indata:
        for i, dataset_uuid_str in enumerate(indata['datasets']):
            dataset_uuid = utils.str_to_uuid(dataset_uuid_str)
            indata['datasets'][i] = dataset_uuid
            # do not reject existing datasets
            if dataset_uuid in project['datasets']:
                continue
            # allow new ones only if owner or DATA_MANAGEMENT
            order_info = flask.g.db['orders'].find_one({'datasets': dataset_uuid})
            if not order_info:
                flask.abort(status=400)
            if not user.has_permission('DATA_MANAGEMENT') and\
               order_info['creator'] != flask.g.current_user['_id'] and\
               order_info['receiver'] != flask.g.current_user['_id']:
                flask.abort(status=400)

    project.update(indata)

    result = flask.g.db['projects'].update_one({'_id': project['_id']}, {'$set': project})
    if not result.acknowledged:
        logging.error('Project update failed: %s', indata)
    else:
        utils.make_log('project', 'edit', 'Project updated', project)

    return flask.Response(status=200)


@blueprint.route('/user/', methods=['GET'])
@user.login_required
def list_user_projects():  # pylint: disable=too-many-branches
    """
    List project owned by the user.

    Returns:
        flask.Response: JSON structure.
    """
    results = list(flask.g.db['projects']
                   .find({'$or': [{'owners': flask.g.current_user['_id']},
                                  {'owners': flask.g.current_user['email']}]}))
    logging.debug(results)
    return utils.response_json({'projects': results})
