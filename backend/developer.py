import flask

import user


blueprint = flask.Blueprint('developer', __name__)

@blueprint.route('/login/<username>')
def login(username):
    user.do_login(username)
    return flask.Response(status=200)


@blueprint.route('/hello')
def api_hello():
    return flask.jsonify({'test': 'success'})


@blueprint.route('/loginhello')
@user.login_required
def login_hello():
    return flask.jsonify({'test': 'success'})


@blueprint.route('/stewardhello')
@user.steward_required
def steward_hello():
    return flask.jsonify({'test': 'success'})


@blueprint.route('/adminhello')
@user.admin_required
def admin_hello():
    return flask.jsonify({'test': 'success'})
