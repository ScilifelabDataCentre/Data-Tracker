import logging
import os

import flask

import config
import datasets
import projects
import user
import utils

app = flask.Flask(__name__)
config.init(app)
logging.debug(app.config)
logging.error(app.config)

@app.before_request
def prepare():
    "Open the database connection; get the current user."
    flask.g.dbserver = utils.get_dbserver()
    flask.g.db = utils.get_db(flask.g.dbserver)
    flask.g.current_user = user.get_current_user()
    flask.g.is_admin = flask.g.current_user and \
                       flask.g.current_user['role'] == constants.ADMIN

@app.after_request
def finalize(response):
    "Close the database connection."
#    flask.g.mongo.close()
    return response

@app.route('/api/hello')
def api_hello():
    logging.error('wtf')
    return flask.jsonify({'test': 'value'})


app.register_blueprint(datasets.blueprint, url_prefix='/api/dataset')
app.register_blueprint(projects.blueprint, url_prefix='/api/project')
