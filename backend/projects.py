import logging
import uuid

import flask

import utils
import user


blueprint = flask.Blueprint('projects', __name__)

@blueprint.route('/all')
def list_project():
    """
    Provide a simplified list of all available projects.
    """
    results = list(flask.g.db['projects'].find())
    utils.clean_mongo(results)
    return flask.jsonify({'projects': results})


@blueprint.route('/add', methods=['POST'])
def add_project():
    """
    Add a project.
    """
    flask.g.db['projects'].insert({'uuid': utils.to_mongo_uuid(uuid.uuid4)})
    return flask.Response(status=200)


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
    result = flask.g.db['projects'].find_one({'uuid': utils.to_mongo_uuid(identifier)})
    if not result:
        flask.Response(status=404)
    utils.clean_mongo(result)
    return flask.jsonify({'project': result})


@blueprint.route('/<identifier>/delete', methods=['PUT'])
def delete_project(identifier):
    return flask.Response(status=500)
