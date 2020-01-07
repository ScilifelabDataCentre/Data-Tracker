import logging

import flask

import db
import utils

blueprint = flask.Blueprint('projects', __name__)


@blueprint.route('/list')
def list_project():
    """
    Provide a simplified list of all available projects.
    """
    result = db.get_projects()
    utils.clean_mongo(result)
    return flask.jsonify({'projects': result})


@blueprint.route('/add', methods=['PUSH'])
def add_project():
    """
    Add a project.
    """
    return flask.Response(status=200)


@blueprint.route('/<identifier>')
def get_project(identifier):
    result = db.get_project(identifier)
    utils.clean_mongo(result)
    return flask.jsonify(result)


@blueprint.route('/<identifier>/delete', methods=['PUT'])
def delete_project(identifier):
    return flask.jsonify(status=500)
