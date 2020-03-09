"""Project requests."""
import logging

import flask

import structure
import user
import utils
import validate

blueprint = flask.Blueprint('project', __name__)  # pylint: disable=invalid-name


@blueprint.route('/', methods=['GET'])
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
    indata = flask.json.loads(flask.request.data)

    # indata validation
    if not validate.validate_indata(indata):
        logging.debug('Validation failed: %s', indata)
        flask.abort(status=400)

    if '_id' in indata:
        logging.debug('Bad field (_id) in indata: %s', indata)
        flask.abort(status=400)

    if 'title' not in indata:
        flask.abort(status=400)

    if 'owners' in indata and indata['owners']:
        if not user.has_permission('DATA_MANAGEMENT'):
            if len(indata['owners']) != 1:
                flask.abort(status=400)
            user_uuid = utils.str_to_uuid(indata['owners'][0])
            if user_uuid != flask.g.current_user['_id']:
                flask.abort(status=400)
    else:
        indata['owners'] = flask.g.current_user['_id']

    if 'datasets' in indata:
        if not user.has_permission('DATA_MANAGEMENT'):
            for ds_uuid_str in indata['datasets']:
                ds_uuid = utils.str_to_uuid(ds_uuid_str)
                order_info = flask.g.db['orders'].find_one({'datasets': ds_uuid})
                if not order_info:
                    flask.abort(status=400)
                if order_info['creator'] != flask.g.current_user['_id'] and\
                   order_info['receiver'] != flask.g.current_user['_id']:
                    flask.abort(status=400)

    for key in indata:
        if key not in project:
            flask.abort(status=400)

    project.update(indata)

    # add to db
    result = flask.g.db['projects'].insert_one(project)
    if not result.acknowledged:
        logging.error('Project insert failed: %s', project)
    else:
        utils.make_log('project', 'add', 'Project added', project)

    return utils.response_json({'_id': result.inserted_id})
