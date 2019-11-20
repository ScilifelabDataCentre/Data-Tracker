import logging
import os

import flask

from settings import SETTINGS
import handlers_datasets as hds

app = flask.Flask(__name__)

if SETTINGS['development_mode']:
    logging.getLogger().setLevel(logging.DEBUG)
    app.config['TESTING'] = True

app.config['SECRET_KEY'] = SETTINGS['flask']['secret']


@app.route('/api/hello')
def api_hello():
    return flask.jsonify({'test': 'value'})


app.register_blueprint(hds.blueprint, url_prefix='/api/dataset')
