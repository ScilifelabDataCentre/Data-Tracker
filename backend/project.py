"""Project requests."""
import flask

import utils


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
