import logging

import flask

import db
import utils

blueprint = flask.Blueprint('datasets', __name__)


@blueprint.route('/hello')
def api_hello():
    return flask.jsonify({'hello': 'world',
                          'from': 'datasets'})


@blueprint.route('/list')
def list_dataset():
    """
    Provide a simplified list of all available datasets.
    """
    result = db.get_datasets()
    utils.clean_mongo(result)
    logging.error(result)
    return flask.jsonify(result)
