"""Dataset requests."""
import json
import logging

import flask

import structure
import utils
import user


blueprint = flask.Blueprint('projects', __name__)  # pylint: disable=invalid-name


def validate_project_input(indata):
    """
    Validate the project input.

    It may only contain valid fields that may be changed by the role of the current user.

    Args:
        indata: the project input

    Returns:
        bool: whether the project input is accepted

    """
    if not utils.check_mongo_update(indata):
        return False
    # check that fields should exist and are not forbidden
    reference = set(structure.project().keys())
    forbidden = {'identifier'}
    inkeys = set(indata.keys())
    if not inkeys.issubset(reference) or forbidden&inkeys:
        logging.debug('Bad input: %s', inkeys)
        return False

    # check restricted (admin/steward) fields
    restricted_steward = {'owner', 'datasets'}
    if not user.check_user_permissions('Steward') and restricted_steward&inkeys:
        logging.debug('Restricted input: %s', inkeys)
        return False

    return True


@blueprint.route('/all', methods=['GET'])
def list_project():
    """Provide a simplified list of all available projects."""
    results = list(flask.g.db['projects'].find())
    return utils.response_json({'projects': results})


@blueprint.route('/random', methods=['GET'])
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
    return utils.response_json({'projects': results})


@blueprint.route('/<identifier>', methods=['GET'])
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
        result = flask.g.db['projects'].find_one({'_id': uuid})
    except ValueError:
        result = None

    if not result:
        return flask.Response(status=404)
    return utils.response_json({'project': result})


@blueprint.route('/add', methods=['GET'])
@user.steward_required
def add_project_get():
    """Provide a basic data structure for adding a project."""
    project = structure.project()
    del project['_id']
    del project['identifiers']
    return utils.response_json(project)


@blueprint.route('/add', methods=['POST'])
@user.steward_required
def add_project_post():
    """Add a project."""
    project = structure.project()

    indata = json.loads(flask.request.data)
    if indata:
        if not validate_project_input(indata):
            flask.abort(flask.Response(status=400))
        project.update(indata)

    if 'datasets' in project:
        try:
            project['datasets'] = [utils.str_to_uuid(ds) for ds in project['datasets']]
        except ValueError:
            flask.abort(flask.Response(status=400))

    result = flask.g.db['projects'].insert_one(project)
    entry = flask.g.db['projects'].find_one({'_id': result.inserted_id},
                                            {'_id': 1})
    return utils.response_json(entry)
