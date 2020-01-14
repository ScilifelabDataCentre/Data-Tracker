import logging
import os

import flask

import config
import datasets
import developer
import projects
import user
import utils


app = flask.Flask(__name__)
config.init(app)

if app.config['dev_mode']:
    app.register_blueprint(developer.blueprint, url_prefix='/api/developer')

app.register_blueprint(datasets.blueprint, url_prefix='/api/dataset')
app.register_blueprint(projects.blueprint, url_prefix='/api/project')
app.register_blueprint(user.blueprint, url_prefix='/api/users')

@app.before_request
def prepare():
    "Open the database connection; get the current user."
    flask.g.dbserver = utils.get_dbserver()
    flask.g.db = utils.get_db(flask.g.dbserver)
    flask.g.current_user = user.get_current_user()
    flask.g.current_role = flask.g.current_user['role'] if flask.g.current_user else None


@app.after_request
def finalize(response):
    "Close the database connection."
    flask.g.dbserver.close()
    return response
