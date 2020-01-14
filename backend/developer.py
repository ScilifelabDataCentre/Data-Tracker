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
    user.do_login(username)
    return flask.Response(status=200)


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
