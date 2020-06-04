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
import functools
import json
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
            flask.abort(status=401)
        return func(*args, **kwargs)
    return wrap


# requests
@blueprint.route('/permissions/')
def get_permission_info():
    """Get a list of all permission types"""
    return flask.jsonify({'permissions': list(PERMISSIONS.keys())})


@blueprint.route('/login/')
@blueprint.route('/login/oidc')
def oidc_login():
    """Perform an Elixir AAI login."""
    return flask.Response(status=501)


# requests
@blueprint.route('/login/apikey/', methods=['POST'])
def key_login():
    """Log in using an apikey."""
    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)

    if 'api-user' not in indata or 'api-key' not in indata:
        logging.debug('API key login - bad keys: %s', indata)
        return flask.Response(status=400)
    utils.verify_api_key(indata['api-user'], indata['api-key'])
    do_login(auth_id=indata['api-user'])
    return flask.Response(status=200)


@blueprint.route('/logout/')
def logout():
    """Log out the current user."""
    flask.session.clear()
    response = flask.redirect("/", code=302)
    response.set_cookie('_csrf_token', utils.gen_csrf_token(), 0)
    return response


@blueprint.route('/')
@login_required
def list_users():
    """
    List all users.

    Admin access should be required.
    """
    if not has_permission('USER_MANAGEMENT'):
        flask.abort(403)
    result = tuple(flask.g.db['users'].find())
    return utils.response_json({'users': result})


# requests
@blueprint.route('/me/')
def get_current_user_info():
    """
    List basic information about the current user.

    Returns:
        flask.Response: json structure for the user
    """
    data = flask.g.current_user
    outstructure = {'affiliation': '',
                    'email': '',
                    'name': '',
                    'permissions': ''}
    if data:
        for field in outstructure:
            if field in data:
                outstructure[field] = data[field]
    return utils.response_json({'user': outstructure})


# requests
@blueprint.route('/me/apikey/', methods=['POST'])
@blueprint.route('/<identifier>/apikey/', methods=['POST'])
@login_required
def gen_new_api_key(identifier: str = None):
    """
    Generate a new API key for the provided or current user.

    Args:
        identifier (str): The uuid of the user.

    Returns:
        flask.Response: The new API key
    """
    if not identifier:
        user_data = flask.g.current_user
    else:
        if not has_permission('USER_MANAGEMENT'):
            flask.abort(403)
        try:
            user_uuid = utils.str_to_uuid(identifier)
        except ValueError:
            flask.abort(status=404)

        if not (user_data := flask.g.db['users'].find_one({'_id': user_uuid})):  # pylint: disable=superfluous-parens
            flask.abort(status=404)

    apikey = utils.gen_api_key()
    new_hash = utils.gen_api_key_hash(apikey.key, apikey.salt)
    new_values = {'api_key': new_hash, 'api_salt': apikey.salt}
    user_data.update(new_values)
    result = flask.g.db['users'].update_one({'_id': user_data['_id']},
                                            {'$set': new_values})
    if not result.acknowledged:
        logging.error('Updating API key for user %s failed', user_data['_id'])
        flask.Response(status=500)
    else:
        utils.make_log('user', 'edit', 'New API key', user_data)

    return utils.response_json({'key': apikey.key})


@blueprint.route('/<identifier>/', methods=['GET'])
@login_required
def get_user_data(identifier: str):
    """
    Get information about a user.

    Args:
        identifier (str): The uuid of the user.

    Returns:
        flask.Response: Information about the user as json.
    """
    if not has_permission('USER_MANAGEMENT'):
        flask.abort(403)

    try:
        user_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    if not (user_info := flask.g.db['users'].find_one({'_id': user_uuid})):  # pylint: disable=superfluous-parens
        flask.abort(status=404)

    return utils.response_json({'user': user_info})


@blueprint.route('/', methods=['POST'])
@login_required
def add_user():
    """
    Add a user.

    Returns:
        flask.Response: Information about the user as json.
    """
    if not has_permission('USER_MANAGEMENT'):
        flask.abort(403)

    new_user = structure.user()
    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)
    validation = utils.basic_check_indata(indata, new_user, ('_id',
                                                             'api_key',
                                                             'api_salt'))
    if not validation[0]:
        flask.abort(status=validation[1])

    if 'auth_id' not in indata:
        flask.abort(status=400)

    new_user.update(indata)

    result = flask.g.db['users'].insert_one(new_user)
    if not result.acknowledged:
        logging.error('User Addition failed: %s', new_user['auth_id'])
        flask.Response(status=500)
    else:
        utils.make_log('user', 'add', 'User added by admin', new_user)

    return utils.response_json({'_id': result.inserted_id})


@blueprint.route('/<identifier>/', methods=['DELETE'])
@login_required
def delete_user(identifier: str):
    """
    Delete a user.

    Args:
        identifier (str): The uuid of the user to modify.

    Returns:
        flask.Response: Response code.
    """
    if not has_permission('USER_MANAGEMENT'):
        flask.abort(403)

    try:
        user_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    if not flask.g.db['users'].find_one({'_id': user_uuid}):
        flask.abort(status=404)

    result = flask.g.db['users'].delete_one({'_id': user_uuid})
    if not result.acknowledged:
        logging.error('User deletion failed: %s', user_uuid)
        flask.Response(status=500)
    else:
        utils.make_log('user', 'delete', 'User delete', {'_id': user_uuid})

    return flask.Response(status=200)


@blueprint.route('/me/', methods=['PATCH'])
@login_required
def update_current_user_info():
    """
    Update the information about the current user.

    Returns:
        flask.Response: Response code.
    """
    user_data = flask.g.current_user

    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)
    validation = utils.basic_check_indata(indata, user_data, ('_id',
                                                              'api_key',
                                                              'api_salt',
                                                              'auth_id',
                                                              'email',
                                                              'permissions'))
    if not validation[0]:
        flask.abort(status=validation[1])

    user_data.update(indata)

    result = flask.g.db['users'].update_one({'_id': user_data['_id']},
                                            {'$set': user_data})
    if not result.acknowledged:
        logging.error('User update failed: %s', indata)
        flask.Response(status=500)
    else:
        utils.make_log('user', 'edit', 'User self-updated', user_data)

    return flask.Response(status=200)


@blueprint.route('/<identifier>/', methods=['PATCH'])
@login_required
def update_user_info(identifier: str):
    """
    Update the information about a user.

    Args:
        identifier (str): The uuid of the user to modify.

    Returns:
        flask.Response: Response code.
    """
    if not has_permission('USER_MANAGEMENT'):
        flask.abort(403)

    try:
        user_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    if not (user_data := flask.g.db['users'].find_one({'_id': user_uuid})):  # pylint: disable=superfluous-parens
        flask.abort(status=404)

    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        flask.abort(status=400)
    validation = utils.basic_check_indata(indata, user_data, ('_id',
                                                              'api_key',
                                                              'api_salt'))
    if not validation[0]:
        flask.abort(status=validation[1])

    if indata:
        result = flask.g.db['users'].update_one({'_id': user_data['_id']},
                                                {'$set': indata})
        if not result.acknowledged:
            logging.error('User update failed: %s', indata)
            flask.Response(status=500)
        else:
            utils.make_log('user', 'edit', 'User updated', user_data)

    return flask.Response(status=200)


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
        user_id (str): The identifier (auth_id) of the user.

    Returns:
        dict: The current user.
    """
    if user_id:
        user = flask.g.db['users'].find_one({'_id': user_id})
        if user:
            return user
    return None


def has_permission(permission: str):
    """
    Check if the current user permissions fulfills the requirement.

    Args:
        permission (str): The required permission

    Returns:
        bool: whether the user has the required permissions or not
    """
    if not flask.g.permissions and permission:
        return False
    user_permissions = set(chain.from_iterable(PERMISSIONS[permission]
                                               for permission in flask.g.permissions))
    if permission not in user_permissions:
        return False
    return True
