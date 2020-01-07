import logging
import os

import flask

import datasets
import projects
from settings import SETTINGS


app = flask.Flask(__name__)

if SETTINGS['development_mode']:
    logging.getLogger().setLevel(logging.DEBUG)
    app.config['TESTING'] = True

app.config['SECRET_KEY'] = SETTINGS['flask']['secret']


@app.route('/api/hello')
def api_hello():
    return flask.jsonify({'test': 'value'})


app.register_blueprint(datasets.blueprint, url_prefix='/api/dataset')
app.register_blueprint(projects.blueprint, url_prefix='/api/project')
