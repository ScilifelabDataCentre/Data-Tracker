import logging

import flask

import db
import utils

blueprint = flask.Blueprint('datasets', __name__)


@blueprint.route('/list')
def list_dataset():
    """
    Provide a simplified list of all available datasets.
    """
    result = db.get_datasets()
    utils.clean_mongo(result)
    return flask.jsonify({'datasets': result})


@blueprint.route('/add', methods=['PUSH'])
def add_dataset():
    """
    Add a dataset.
    """
    return flask.Response(status=200)


@blueprint.route('/<identifier>')
def get_dataset(identifier):
    result = db.get_dataset(identifier)
    utils.clean_mongo(result)
    return flask.jsonify(result)


@blueprint.route('/<identifier>/delete', methods=['PUT'])
def delete_dataset(identifier):
    return flask.jsonify(status=500)
