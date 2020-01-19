"""User profile and login/logout HTMl endpoints."""

import functools
import logging

import flask

import structure
import utils


blueprint = flask.Blueprint('user', __name__)  # pylint: disable=invalid-name


# Decorators
def login_required(func):
    """
    Confirm that the user is logged in.

    Otherwise abort with status 401 Unauthorized.
    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if not flask.g.current_user:
            flask.abort(flask.Response(status=401))
        return func(*args, **kwargs)
    return wrap


def steward_required(func):
    """
    Confirm that the user is logged in and has the 'Steward' role.

    Otherwise abort with status 401 Unauthorized.
    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if not check_user_permissions('Steward'):
            flask.abort(flask.Response(status=401))
        return func(*args, **kwargs)
    return wrap


def steward_or_owner_required(func, dec_dataset=None, dec_project=None):
    """
    Confirm that the user is logged in and has the 'Steward' role.

    Otherwise abort with status 401 Unauthorized.
    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if not check_user_permissions('Steward')\
        and not utils.is_owner(dec_dataset, dec_project):
            flask.abort(flask.Response(status=401))
        return func(*args, **kwargs)
    return wrap


def admin_required(func):
    """
    Confirm that the user is logged in and has the 'Admin' role.

    Otherwise return status 401 Unauthorized.
    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if not check_user_permissions('Admin'):
            flask.abort(flask.Response(status=401))
        return func(*args, **kwargs)
    return wrap


def check_user_permissions(required: str):
    """
    Check if the current permissions fulfills the requirement.

    Args:
        required (str): the required role

    Returns:
        bool: whether the user has the required permissions or not

    """
    roles = ['User', 'Steward', 'Admin']
    if (role := flask.g.current_role) not in roles:
        logging.warning('Unknown user role: %s', role)
        return False
    if roles.index(flask.g.current_role) >= roles.index(required):
        return True

    logging.warning('Rejected access. User: %s ',
                    flask.g.current_user)
    return False



# requests
@blueprint.route('/login')
def elixir_login():
    """Perform a Elixir AAI login."""
    return flask.Response(status=500)


@blueprint.route('/logout')
def logout():
    """Log out the current user."""
    if 'username' in flask.session:
        del flask.session['username']
    response = flask.Response(status=200)
    response.set_cookie('_csrf_token', '', expires=0)
    return response


@blueprint.route('/all')
@admin_required
def list_users():
    """
    List all users.

    Admin access should be required.
    """
    result = list(flask.g.db['users'].find())
    utils.clean_mongo(result)
    return flask.jsonify({'users': result})


# requests
@blueprint.route('/me')
def get_current_user_info():
    """
    List basic information about the current user.

    Returns:
        flask.Response: json structure for the user

    """
    return flask.Response(status=500)


# helper functions
def do_login(username: str):
    """
    Set all relevant variables for a logged in user.

    Users not in db will be added.

    Args:
        username (str): The username (email) of the user
    """
    result = flask.g.db['users'].find_one({'email': username})
    if not result:
        user = structure.user()
        user['email'] = username
        flask.g.db['user'].insert(user)

    flask.session['username'] = username
    flask.session.permanent = True
    response = flask.Response(status=200)
    response.set_cookie('_csrf_token', utils.gen_csrf_token(), samesite='Lax')
    return response


def get_current_user():
    """
    Get the current user.

    Returns:
        dict: the current user
    """
    return get_user(username=flask.session.get('username'))


def get_user(username=None, apikey=None):
    """
    Get data about the user.

    Args:
        username (str): The username (email) of the user
        apikey (str): The api key of the user

    Returns:
        dict: The current user

    """
    usercoll = flask.g.db['users']
    if username:
        user = usercoll.find_one({'email': username})
        if user:
            return user
    if apikey:
        user = usercoll.find_one({'apikey': apikey})
        if user:
            return user
    return None
