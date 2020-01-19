"""Routes and functions intended to aid development and testing."""

import flask

import user

blueprint = flask.Blueprint('developer', __name__)  # pylint: disable=invalid-name


@blueprint.route('/login/<username>')
def login(username: str):
    """
    Log in without password.

    Args:
        username (str): the user (email) to log in as
    """
    response = user.do_login(username)
    return response


@blueprint.route('/hello')
def api_hello():
    """Test request."""
    return flask.jsonify({'test': 'success'})


@blueprint.route('/loginhello')
@user.login_required
def login_hello():
    """Test request requiring login."""
    return flask.jsonify({'test': 'success'})


@blueprint.route('/stewardhello')
@user.steward_required
def steward_hello():
    """Test request requiring Steward rights."""
    return flask.jsonify({'test': 'success'})


@blueprint.route('/adminhello')
@user.admin_required
def admin_hello():
    """Test request requiring Admin rights."""
    return flask.jsonify({'test': 'success'})


@blueprint.route('/csrftest', methods=['POST', 'PUT', 'DELETE'])
def csrf_test():
    """Test csrf tokens."""
    return flask.jsonify({'test': 'success'})


@blueprint.route('/test_datasets')
def get_added_ds():
    """Get datasets added during testing."""
    added = list(flask.g.db['datasets'].find({'dmp': 'http://test'},
                                             {'uuid': 1, '_id': 0}))
    return flask.jsonify({'datasets': added})


@blueprint.route('/quit')
def stop_server():
    """Shutdown the flask server."""
    flask.request.environ.get('werkzeug.server.shutdown')()
    return flask.Response(status=200)
