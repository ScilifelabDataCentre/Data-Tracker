"""
User profile, permissions, and login/logout functions and endpoints.

Decorators
    Decorators used to e.g. assert that a user is logged in.

Helper functions
    Functions to help with user-related tasks, e.g. setting all variables at login.

Requests
    User-related API endpoints, including login/logout and user manament.
"""
from itertools import chain
from typing import Union  # pylint: disable=unused-import
import functools
import logging

import flask

import structure
import utils


blueprint = flask.Blueprint('user', __name__)  # pylint: disable=invalid-name

PERMISSIONS = {'ORDERS_SELF': ('ORDERS_SELF',),
               'OWNERS_READ': ('OWNERS_READ',),
               'USER_MANAGEMENT': ('USER_MANAGEMENT',),
               'DATA_MANAGEMENT': ('ORDERS_SELF', 'OWNERS_READ', 'DATA_MANAGEMENT'),
               'DOI_REVIEWER': ('DOI_REVIEWER',)}


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
            flask.abort(flask.Response(status=403))
        return func(*args, **kwargs)
    return wrap


def steward_or_dsowner_required(func):
    """
    Confirm that the user is logged in and has the 'Steward' role.

    Otherwise abort with status 401 Unauthorized.
    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        if not check_user_permissions('Steward')\
           and not utils.is_owner(dataset=kwargs['identifier']):
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


# requests
@blueprint.route('/login')
def elixir_login():
    """Perform a Elixir AAI login."""
    return flask.Response(status=501)


@blueprint.route('/logout')
def logout():
    """Log out the current user."""
    flask.session.clear()
    response = flask.redirect("/", code=302)
    response.set_cookie('_csrf_token', utils.gen_csrf_token(), 0)
    return response


@blueprint.route('/all')
@admin_required
def list_users():
    """
    List all users.

    Admin access should be required.
    """
    result = tuple(flask.g.db['users'].find())
    return utils.response_json({'users': result})


# requests
@blueprint.route('/me')
def get_current_user_info():
    """
    List basic information about the current user.

    Returns:
        flask.Response: json structure for the user

    """
    data = flask.g.current_user
    outstructure = {'affiliation': '',
                    'country': '',
                    'email': '',
                    'name': '',
                    'role': ''}
    if data:
        for field in outstructure:
            if field in data:
                outstructure[field] = data[field]
    return flask.jsonify({'user': outstructure})


# helper functions
def do_login(*, auth_id: str = None, api_key: str = None):
    """
    Set all relevant variables for a logged in user.

    Users not in db will be added.

    Args:
        auth_id (str): Authentication id for the user.
        api_key (str): API key for the user.

    Returns bool: Whether the login succeeded.
    """
    if auth_id:
        user = flask.g.db['users'].find_one({'auth_id': auth_id})
    elif api_key:
        user = flask.g.db['users'].find_one({'api_key': api_key})
    else:
        user = structure.user()
        user['auth_id'] = auth_id
        user['api_key'] = api_key
        response = flask.g.db['users'].insert_one(user)
        if not response.acknowledged:
            logging.error(f'Failed to write user to db: {user}')

    flask.session['user_id'] = user['_id']
    flask.session.permanent = True
    return True


def get_current_user():
    """
    Get the current user.

    Returns:
        dict: The current user.
    """
    return get_user(user_id=flask.session.get('user_id'))


def get_user(user_id=None):
    """
    Get information about the user.

    Args:
        user_aid (str): The identifier (auth_id) of the user.

    Returns:
        dict: The current user.
    """
    if user_id:
        user = flask.g.db['users'].find_one({'_id': user_id})
        if user:
            return user
    return None


def check_user_permissions(required: str):
    """
    Check if the current permissions fulfills the requirement.

    Args:
        required (str): the required permission

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


def has_permission(permission: str):
    """
    Check if the current user permissions fulfills the requirement.

    Args:
        permission (str): The required permission

    Returns:
        bool: whether the user has the required permissions or not
    """
    user_permissions = set(chain.from_iterable(PERMISSIONS[permission]
                                               for permission in flask.g.permissions))
    if permission not in user_permissions:
        return False
    return True
