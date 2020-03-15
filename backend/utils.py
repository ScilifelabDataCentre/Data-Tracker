"""General helper functions."""

from collections import abc
from typing import Any, Union
import datetime
import logging
import re
import uuid

import bson
import flask
import pymongo

import structure
import validate


def basic_check_indata(indata: dict,
                       reference_data: dict,
                       prohibited: Union[tuple, list]) -> tuple:
    """
    Perform basic checks of indata.

    * All fields are allowed in the entity type
    * All fields are of the correct type
    * All prohibited fields are unchanged (if update)

    Args:
        indata (dict): The incoming data.
        reference_data (dict): Either the old data or a reference dict.
        prohibited (Union[tuple, list]): Fields that may not be modified.
            If they are included in ``indata``, their values must be equal to the 
            values in ``reference_data``. Defaults to ``None``.

    Returns:
        tuple: (``bool``: hether the check passed, ``code``: Suggested http code)
    """
    if prohibited is None:
        prohibited = []

    if 'title' in reference_data:
        if not reference_data['title'] and 'title' not in indata:
            return (False, 400)

    for key in indata:
        if key in prohibited:
            if indata[key] != reference_data[key]:
                return (False, 403)
        if key not in reference_data:
            return (False, 400)
        if not validate.validate_field(key, indata[key]):
            logging.debug('correct')
            return (False, 400)
    return (True, 200)


# csrf
def verify_csrf_token():
    """Compare the csrf token from the request (header) with the one in the cookie.session."""
    token = flask.request.headers.get('X-CSRFToken')
    if not token or (token != flask.request.cookies.get('_csrf_token')):
        logging.warning('Bad csrf token received')
        flask.abort(flask.Response(status=400))


def gen_csrf_token() -> str:
    """
    Genereate a csrf token.

    Returns:
        str: The csrf token.

    """
    return uuid.uuid4().hex


def get_dbclient(conf) -> pymongo.mongo_client.MongoClient:
    """
    Get the connection to the MongoDB database server.

    Args:
        conf: A mapping with the relevant mongo keys available.

    Returns:
        pymongo.mongo_client.MongoClient: The client connection.
    """
    return pymongo.MongoClient(host=conf['mongo']['host'],
                               port=conf['mongo']['port'],
                               username=conf['mongo']['user'],
                               password=conf['mongo']['password'])


def get_db(dbserver: pymongo.mongo_client.MongoClient, conf) -> pymongo.database.Database:
    """
    Get the connection to the MongoDB database.

    Args:
        dbserver (pymongo.mongo_client.MongoClient): Connection to the database.
        conf: A mapping with the relevant mongo keys available.

    Returns:
        pymongo.database.Database: The database connection.
    """
    codec_options = bson.codec_options.CodecOptions(uuid_representation=bson.binary.STANDARD)
    return dbserver.get_database(conf['mongo']['db'],
                                 codec_options=(codec_options))


def new_uuid() -> uuid.UUID:
    """
    Generate a uuid for a field in a MongoDB document.

    Returns:
        uuid.UUID: The new uuid in binary format.
    """
    return uuid.uuid4()


def str_to_uuid(uuid_str: str) -> uuid.UUID:
    """
    Convert str uuid to uuid.UUID.

    Provided as a convenience function if the identifier must be changed in the future.

    Args:
        uuid_str (str): The uuid to be converted.

    Returns:
        uuid.UUID: The uuid.
    """
    return uuid.UUID(uuid_str)


# misc
def convert_keys_to_camel(chunk: Any) -> Any:
    """
    Convert keys given in snake_case to camelCase.

    The capitalization of the first letter is preserved.

    Args:
        chunk (Any): Object to convert.

    Returns:
        Any: Chunk converted to camelCase `dict`, otherwise chunk.
    """
    if isinstance(chunk, abc.Sequence) and not isinstance(chunk, str):
        return [convert_keys_to_camel(e) for e in chunk]

    if not isinstance(chunk, abc.Mapping):
        return chunk

    new_chunk = {}
    for key, value in chunk.items():
        if key == '_id':
            new_chunk[key] = value
            continue
        # First character should be the same as in the original string
        new_key = key[0] + "".join([a[0].upper() + a[1:] for a in key.split("_")])[1:]
        new_chunk[new_key] = convert_keys_to_camel(value)
    return new_chunk


REGEX = {'email': re.compile(r'.*@.*\..*')}


def is_email(indata: str):
    """
    Check whether a string seems to be an email address or not.

    Args:
        indata (str): Data to check.

    Returns:
        bool: Is the indata an email address or not.
    """
    return bool(REGEX['email'].search(indata))


def is_owner(dataset: str = None, project: str = None):
    """
    Check if the current user owns the given dataset or project.

    If both a dataset and a project is provided, an exception will be raised.

    Args:
        dataset (str): the dataset to check
        project (str): the project to check

    Returns:
        bool: whether the current owns the dataset/project

    Raises:
        ValueError: one of dataset or project must be set, and not both
    """
    if dataset and project:
        raise ValueError('Only one of dataset and project should be set')
    if dataset:
        try:
            muuid = str_to_uuid(dataset)
        except ValueError:
            flask.abort(flask.Response(status=401))
        projects = list(flask.g.db['projects'].find({'datasets': muuid},
                                                    {'owner': 1, 'datasets': 1, '_id': 0}))
        owners = [project['owner'] for project in projects]
    elif project:
        proj_data = get_project(project)
        if not proj_data:
            flask.abort(status=404)
        owners = [project['owner']]
    else:
        raise ValueError('Either dataset or project must be set')

    if flask.g.current_user['email'] in owners:
        return True
    return False


def response_json(json_structure: dict):
    """
    Convert keys to camelCase and run ``flask.jsonify()``.

    Args:
        json_structure (dict): Structure to prepare.

    Returns:
        flask.Response: Prepared response containing json structure with camelBack keys.
    """
    data = convert_keys_to_camel(json_structure)
    return flask.jsonify(data)


def make_timestamp():
    """
    Generate a timestamp of the current time.

    returns:
        datetime.datetime: The current time.
    """
    return datetime.datetime.now()


def make_log(data_type: str, action: str, comment: str, data: dict = None):
    """
    Log a change in the system.

    Saves a complete copy of the new object.

    Warning:
        It is assumed that all values are exactly like in the db,
        e.g. ``data`` should only contain permitted fields.

    Args:
        action (str): Type of action (add, edit, delete).
        comment (str): Note about why the change was done
            (e.g. "Dataset added via addDataset").
        data_type (str): The collection name.
        data (dict): The new data for the entry.

    Returns:
        bool: Whether the log insertion successed.
    """
    log = structure.log()
    log.update({'action': action,
                'comment': comment,
                'data_type': data_type,
                'data': data,
                'user': flask.g.current_user['_id']})
    result = flask.g.db['logs'].insert_one(log)
    if not result.acknowledged:
        logging.error(f'Log failed: A:{action} C:{comment} D:{data} ' +
                      f'DT: {data_type} U: {flask.g.current_user["_id"]}')
    return result.acknowledged


def incremental_logs(logs: list):
    """
    Make an incremental log.

    The log starts from the first log and keeps only
    the changed fields in ``data``.

    ``logs`` is changed in-place.
    """
    logs.sort(key=lambda x: x['timestamp'])
    for i in range(len(logs)-1, 0, -1):
        del_keys = []
        for key in logs[i]['data']:
            if logs[i]['data'][key] == logs[i-1]['data'][key]:
                del_keys.append(key)
        for key in del_keys:
            del logs[i]['data'][key]


def check_email_uuid(user_identifier: str) -> Union[str, uuid.UUID]:
    """
    Check if the provided user is found in the db as email or _id.

    If the user is found, return the user.UUID of the user.
    If the identifier is a uuid, return a user.UUID.
    If the identifier is an email, return the email.

    Notes:
       ``user_identifier`` is assumed to be either a valid email or a valid uuid.

    Args:
        user_identifier (str): The identifier to look up.

    Returns:
        Union[str, uuid.UUID]: The new value for the field.
    """
    if is_email(user_identifier):
        user_entry = flask.g.db['users'].find_one({'email': user_identifier})
        if user_entry:
            return user_entry['_id']
        return user_identifier
    user_entry = flask.g.db['users'].find_one({'_id': str_to_uuid(user_identifier)})
    if user_entry:
        return user_entry['_id']
    return ''
