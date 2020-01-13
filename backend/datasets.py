import logging
import uuid

import flask

import utils
import user


blueprint = flask.Blueprint('datasets', __name__)

@blueprint.route('/all')
def list_dataset():
    """
    Provide a simplified list of all available datasets.
    """
    results = list(flask.g.db['datasets'].find())
    utils.clean_mongo(results)
    return flask.jsonify({'datasets': results})


@blueprint.route('/add', methods=['POST'])
def add_dataset():
    """
    Add a dataset.
    """
    flask.g.db['datasets'].insert({'uuid': utils.to_mongo_uuid(uuid.uuid4)})
    return flask.Response(status=200)


@blueprint.route('/random')
@blueprint.route('/random/<int:amount>')
def get_random_ds(amount: int = 1):
    """
    Retrieve random dataset(s).

    Args:
        amount (int): number of requested datasets

    Returns:
        flask.Request: json structure for the dataset(s)

    """
    results = list(flask.g.db['datasets'].aggregate([{'$sample': {'size': amount}}]))
    utils.clean_mongo(results)
    return flask.jsonify({'datasets': results})


@blueprint.route('/<identifier>')
def get_dataset(identifier):
    """
    Retrieve the dataset with uuid <identifier>.

    Args:
        identifier (str): uuid for the wanted dataset

    Returns:
        flask.Request: json structure for the dataset

    """
    result = flask.g.db['datasets'].find_one({'uuid': utils.to_mongo_uuid(identifier)})
    if not result:
        flask.Response(status=404)
    utils.clean_mongo(result)
    return flask.jsonify({'dataset': result})


@blueprint.route('/<identifier>/delete', methods=['PUT'])
def delete_dataset(identifier):
    return flask.Response(status=500)
