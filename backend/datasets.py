import logging

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
    return flask.Response(status=200)


@blueprint.route('/<identifier>')
def get_dataset(identifier):
    result = flask.g.db['datasets'].find_one({'id': int(identifier)})
    utils.clean_mongo(result)
    return flask.jsonify({'dataset': result})


@blueprint.route('/<identifier>/delete', methods=['PUT'])
def delete_dataset(identifier):
    return flask.jsonify(status=500)
