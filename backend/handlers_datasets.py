import logging

import flask

blueprint = flask.Blueprint('datasets', __name__)

@blueprint.route('/hello')
def api_hello():
    return flask.jsonify({'hello': 'world',
                          'from': 'datasets'})

