import logging

import flask

from .settings import SETTINGS

app = flask.Flask('backend')

if SETTINGS['development_mode']:
    logging.getLogger().setLevel(logging.DEBUG)
    app.config['TESTING'] = True

app.config['SECRET_KEY'] = SETTINGS['flask']['flask_secret']

@app.route('/api/hello')
def api_hello():
    return flask.jsonify({'test': 'value'})

def list_datasets():
    """
    Provide a simplified list of all available datasets.
    """

    return flask.jsonify()
