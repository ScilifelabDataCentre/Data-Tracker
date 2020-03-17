"""
Validators for indata.

Indata can be sent to ``validate_indata``, which will use the corresponding
functions to check each field.
"""
from typing import Any, Union
import logging
import uuid

import flask

from user import PERMISSIONS
import utils

def validate_field(field_key: str, field_value: Any) -> bool:
    """
    Validate that the input data matches expectations.

    Will check the data based on the key.

    The validation is only done at the technical level,
    e.g. a check that input is of the correct type.

    Checks for e.g. permissions and that the correct fields are provided
    for the entry must be performed separately.

    Args:
        field_key (str): The field to validate.
        field_value (Any): The value to validate.

    Returns:
        bool: Whether validation passed.
    """
    try:
        VALIDATION_MAPPER[field_key](field_value)
    except KeyError as err:
        logging.debug('Unknown key: %s', field_key)
        return False
    except ValueError as err:
        logging.debug('Indata validation failed: %s - %s', field_key, err)
        return False
    return True


def validate_datasets(data: list) -> bool:
    """
    Validate input for the ``datasets`` field.

    It must be a list of uuids. Validate that the datasets exist in the db.

    Args:
        data (str): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    for ds_entry in data:
        try:
            ds_uuid = uuid.UUID(ds_entry)
        except ValueError:
            raise ValueError(f'Not a valid uuid ({data})')
        if not flask.g.db['datasets'].find_one({'_id': ds_uuid}):
            raise ValueError(f'Uuid not in db ({data})')
        return True


def validate_email(data) -> bool:
    """
    Validate input for the ``email`` field.

    It must be a string.

    Args:
        data: The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, str):
        raise ValueError(f'Not a string ({data})')
    if not utils.is_email(data):
        raise ValueError(f'Not a valid email address ({data})')
    return True


def validate_extra(data) -> bool:
    """
    Validate input for the ``extra`` field.

    It must be a string.

    Args:
        data: The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, dict):
        raise ValueError(f'Must be dict ({data})')
    for key in data:
        if not isinstance(key, str) or not isinstance(data[key], str):
            raise ValueError(f'Keys and values must be strings ({key}, {data[key]})')
    return True


def validate_links(data: list) -> bool:
    """
    Validate input for the ``links`` field.

    It must have the form ``[{'url': value, 'description': value}, ...]``.

    Args:
        data: The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, list):
        raise ValueError('Must be a list')
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError('Must be a list of dicts')
        for key in entry:
            if key not in ('url', 'description'):
                raise ValueError('Bad key in dict')
            if not isinstance(entry[key], str):
                raise ValueError('Values must be type str')
    return True


def validate_permissions(data: list) -> bool:
    """
    Validate input for the ``permissions`` field.

    It must be a list containing permissions found in ``PERMISSIONS``.

    Args:
        data (list): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, list):
        raise ValueError('Must be a list')
    for entry in data:
        if entry not in PERMISSIONS:
            raise ValueError(f'Bad entry ({entry})')
    return True


def validate_publications(data: list) -> bool:
    """
    Validate input for the ``publications`` field.

    It must have the form ``[{'title': value, 'doi': value}, ...]``.

    Args:
        data (list): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, list):
        raise ValueError('Must be a list')
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError('Must be a list of dicts')
        for key in entry:
            if key not in ('title', 'doi'):
                raise ValueError('Bad key in dict')
            if not isinstance(entry[key], str):
                raise ValueError('Values must be type str')
    return True


def validate_string(data: str) -> bool:
    """
    Validate input for field that must have a ``str`` value.

    Args:
        data: The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, str):
        raise ValueError(f'Not a string ({data})')
    return True


def validate_title(data: str) -> bool:
    """
    Validate input for the ``title`` field.

    It must be a non-empty string.

    Args:
        data: The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if validate_string(data):
        if not data:
            raise ValueError('Must not be empty')
    return True


def validate_user(data: Union[str, list]) -> bool:
    """
    Validate input for the ``title`` field.

    It must be a non-empty string.
    If uuid, confirms that uuid is present in db.

    Args:
        data (Union[str, list]): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if isinstance(data, str):
        user_uuids = [data]
    elif isinstance(data, list):
        user_uuids = data
    else:
        raise ValueError(f'Bad data type ({data})')
    # Non-registered user (email instead of uuid)
    for u_uuid in user_uuids:
        if utils.is_email(u_uuid):
            return True
        try:
            user_uuid = uuid.UUID(u_uuid)
        except ValueError:
            raise ValueError(f'Not a valid uuid ({data})')
        if not flask.g.db['users'].find_one({'_id': user_uuid}):
            raise ValueError(f'Uuid not in db ({data})')
        return True


VALIDATION_MAPPER = {'affiliation': validate_string,
                     'api_key': validate_string,
                     'auth_id': validate_string,
                     'contact': validate_string,
                     'description': validate_string,
                     'dmp': validate_string,
                     'name': validate_string,
                     'creator': validate_user,
                     'receiver': validate_user,
                     'datasets': validate_datasets,
                     'email': validate_email,
                     'extra': validate_extra,
                     'links': validate_links,
                     'owners': validate_user,
                     'permissions': validate_permissions,
                     'publications': validate_publications,
                     'title': validate_title}
