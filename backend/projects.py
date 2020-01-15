"""Project requests."""

import logging

import flask

import structure
import utils
import user


blueprint = flask.Blueprint('projects', __name__)  # pylint: disable=invalid-name

@blueprint.route('/all')
def list_project():
    """
    Provide a simplified list of all available projects.
    """
    results = list(flask.g.db['projects'].find())
    utils.clean_mongo(results)
    return flask.jsonify({'projects': results})


@blueprint.route('/add', methods=['POST'])
@user.steward_required
def add_project():
    """
    Add a project.
    """
    project = structure.project()
    result = flask.g.db['projects'].insert_one(project)
    inserted = flask.g.db['projects'].find_one({'_id': result.inserted_id})
    return flask.jsonify({'uuid': inserted['uuid']})


@blueprint.route('/random')
@blueprint.route('/random/<int:amount>')
def get_random_ds(amount: int = 1):
    """
    Retrieve random project(s).

    Args:
        amount (int): number of requested projects

    Returns:
        flask.Request: json structure for the project(s)

    """
    results = list(flask.g.db['projects'].aggregate([{'$sample': {'size': amount}}]))
    utils.clean_mongo(results)
    return flask.jsonify({'projects': results})


@blueprint.route('/<identifier>')
def get_project(identifier):
    """
    Retrieve the project with uuid <identifier>.

    Args:
        identifier (str): uuid for the wanted project

    Returns:
        flask.Request: json structure for the project

    """
    try:
        mongo_uuid = utils.to_mongo_uuid(identifier)
        result = flask.g.db['projects'].find_one({'uuid': mongo_uuid})
    except ValueError:
        result = None

    if not result:
        return flask.Response(status=404)
    utils.clean_mongo(result)
    return flask.jsonify({'project': result})


@blueprint.route('/<identifier>/delete', methods=['PUT'])
@user.steward_required
def delete_project(identifier):
    """Delete a project."""
    try:
        mongo_uuid = utils.to_mongo_uuid(identifier)
    except ValueError:
        return flask.Response(status=404)
    result = flask.g.db['projects'].delete_one({'uuid': mongo_uuid})
    if result.deleted_count == 0:
        return flask.Response(status=404)
    return flask.Response(status=200)
