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

PERMISSIONS = {'ORDERS': ('ORDERS', 'USER_ADD', 'USER_SEARCH'),
               'OWNERS_READ': ('OWNERS_READ',),
               'USER_ADD': ('USER_ADD',),
               'USER_SEARCH': ('USER_SEARCH',),
               'USER_MANAGEMENT': ('USER_MANAGEMENT', 'USER_ADD', 'USER_SEARCH'),
               'DATA_MANAGEMENT': ('ORDERS', 'OWNERS_READ', 'DATA_MANAGEMENT')}


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
    """Get a list of all permission types."""
    return utils.response_json({'permissions': list(PERMISSIONS.keys())})


@blueprint.route('/')
@login_required
def list_users():
    """
    List all users.

    Admin access should be required.
    """
    if not has_permission('USER_SEARCH'):
        flask.abort(403)

    fields = {'api_key': 0,
              'api_salt': 0}

    if not has_permission('USER_MANAGEMENT'):
        fields['auth_ids'] = 0
        fields['permissions'] = 0

    result = tuple(flask.g.db['users'].find(projection=fields))

    return utils.response_json({'users': result})


@blueprint.route('/structure/', methods=['GET'])
def get_user_data_structure():
    """
    Get an empty user entry.

    Returns:
        flask.Response: JSON structure with a list of users.
    """
    empty_user = structure.user()
    empty_user['_id'] = ''
    return utils.response_json({'user': empty_user})


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
                    'auth_ids': [],
                    'email': '',
                    'contact': '',
                    'name': '',
                    'orcid': '',
                    'permissions': '',
                    'url': ''}
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

    # The hash and salt should never leave the system
    del user_info['api_key']
    del user_info['api_salt']

    return utils.response_json({'user': user_info})


@blueprint.route('/', methods=['POST'])
@login_required
def add_user():
    """
    Add a user.

    Returns:
        flask.Response: Information about the user as json.
    """
    if not has_permission('USER_ADD'):
        flask.abort(403)

    new_user = structure.user()
    try:
        indata = flask.json.loads(flask.request.data)
    except json.decoder.JSONDecodeError:
        logging.error('Bad JSON')
        flask.abort(status=400)
    validation = utils.basic_check_indata(indata, new_user, ('_id',
                                                             'api_key',
                                                             'api_salt',
                                                             'auth_ids'))
    if not validation.result:
        flask.abort(status=validation.status)

    new_user.update(indata)

    new_user['auth_ids'] = [f'{new_user["_id"]::local']

    result = flask.g.db['users'].insert_one(new_user)
    if not result.acknowledged:
        logging.error('User Addition failed: %s', new_user['email'])
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
                                                              'auth_ids',
                                                              'email',
                                                              'permissions'))
    if not validation[0]:
        flask.abort(status=validation[1])

    user_data.update(indata)

    result = flask.g.db['users'].update_one({'_id': user_data['_id']},
                                            {'$set': user_data})
    if not result.acknowledged:
        logging.error('User self-update failed: %s', indata)
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

    # Avoid "updating" and making log if there are no changes
    is_different = False
    for field in indata:
        if indata[field] != user_data[field]:
            is_different = True
            break

    if indata and is_different:
        result = flask.g.db['users'].update_one({'_id': user_data['_id']},
                                                {'$set': indata})
        if not result.acknowledged:
            logging.error('User update failed: %s', indata)
            flask.Response(status=500)
        else:
            user_data.update(indata)
            utils.make_log('user', 'edit', 'User updated', user_data)

    return flask.Response(status=200)


@blueprint.route('/me/log/', methods=['GET'])
@blueprint.route('/<identifier>/log/', methods=['GET'])
@login_required
def get_user_log(identifier: str = None):
    """
    Get change logs for the user entry with uuid ``identifier``.

    Can be accessed by actual user and admin (USER_MANAGEMENT).

    Args:
        identifier (str): The uuid of the user.

    Returns:
        flask.Response: Information about the user as json.
    """
    if identifier is None:
        identifier = str(flask.g.current_user['_id'])

    if str(flask.g.current_user['_id']) != identifier and not has_permission('USER_MANAGEMENT'):
        flask.abort(403)

    try:
        user_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    user_logs = list(flask.g.db['logs'].find({'data_type': 'user', 'data._id': user_uuid}))

    for log in user_logs:
        del log['data_type']

    utils.incremental_logs(user_logs)

    return utils.response_json({'entry_id': user_uuid,
                                'data_type': 'user',
                                'logs': user_logs})


@blueprint.route('/me/actions/', methods=['GET'])
@blueprint.route('/<identifier>/actions/', methods=['GET'])
@login_required
def get_user_actions(identifier: str = None):
    """
    Get a list of actions (changes) by the user entry with uuid ``identifier``.

    Can be accessed by actual user and admin (USER_MANAGEMENT).

    Args:
        identifier (str): The uuid of the user.

    Returns:
        flask.Response: Information about the user as json.
    """
    if identifier is None:
        identifier = str(flask.g.current_user['_id'])

    if str(flask.g.current_user['_id']) != identifier and not has_permission('USER_MANAGEMENT'):
        flask.abort(403)

    try:
        user_uuid = utils.str_to_uuid(identifier)
    except ValueError:
        flask.abort(status=404)

    # only report a list of actions, not the actual data
    user_logs = list(flask.g.db['logs'].find({'user': user_uuid}, {'user': 0}))

    for entry in user_logs:
        entry['entry_id'] = entry['data']['_id']
        del entry['data']

    return utils.response_json({'logs': user_logs})


# helper functions
def add_new_user(user_info: dict):
    """
    Add a new user to the database from first oidc login.

    First check if user with the same email exists.
    If so, add the auth_id to the user.

    Args:
        user_info (dict): Information about the user
    """
    email_user = flask.g.db['users'].find_one({'email': user_info['email']})
    if email_user:
        email_user['auth_ids'].append(user_info['auth_id'])
        result = flask.g.db['users'].update_one({'email': user_info['email']},
                                                {'$set': {'auth_ids': email_user['auth_ids']}})
        if not result.acknowledged:
            logging.error('Failed to add new auth_id to user with email %s', user_info['email'])
            flask.Response(status=500)
        else:
            utils.make_log('user',
                           'edit',
                           'Edit entry to auth_ids to user from OAuth',
                           email_user,
                           no_user=True)

    else:
        new_user = structure.user()
        new_user['email'] = user_info['email']
        new_user['name'] = user_info['name']
        new_user['auth_ids'] = [user_info['auth_id']]

        result = flask.g.db['users'].insert_one(new_user)
        if not result.acknowledged:
            logging.error('Failed to add user with email %s via oidc', user_info['email'])
            flask.Response(status=500)
        else:
            utils.make_log('user', 'add', 'Creating new user from OAuth', new_user, no_user=True)


def do_login(auth_id: str):
    """
    Set all relevant variables for a logged in user.

    Args:
        auth_id (str): Authentication id for the user.

    Returns bool: Whether the login succeeded.
    """
    user = flask.g.db['users'].find_one({'auth_ids': auth_id})

    if not user:
        return False

    flask.session['user_id'] = user['_id']
    flask.session.permanent = True
    return True


def get_current_user():
    """
    Get the current user.

    Returns:
        dict: The current user.
    """
    return get_user(user_uuid=flask.session.get('user_id'))


def get_user(user_uuid=None):
    """
    Get information about the user.

    Args:
        user_uuid (str): The identifier (uuid) of the user.

    Returns:
        dict: The current user.
    """
    if user_uuid:
        user = flask.g.db['users'].find_one({'_id': user_uuid})
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
