"""
Validators for indata.

Indata can be sent to ``validate_field``, which will use the corresponding
functions to check each field.
"""
import logging
from typing import Any, Union
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
    except KeyError:
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
    if not isinstance(data, list):
        raise ValueError(f'Must be list ({data})')
    for ds_entry in data:
        if not isinstance(ds_entry, str):
            raise ValueError(f'Must be str ({ds_entry})')
        try:
            ds_uuid = uuid.UUID(ds_entry)
        except ValueError as err:
            raise ValueError(f'Not a valid uuid ({data})') from err
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


def validate_list_of_strings(data: list) -> bool:
    """
    Validate that input is a list of strings.

    Args:
        data (list): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, list):
        raise ValueError(f'Not a list ({data})')
    for entry in data:
        if not isinstance(entry, str):
            raise ValueError(f'Not a string ({entry})')
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


def validate_string(data: str) -> bool:
    """
    Validate input for field that must have a ``str`` value.

    Args:
        data (str): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, str):
        raise ValueError(f'Not a string ({data})')
    return True


def validate_tags_std(data: dict) -> bool:
    """
    Validate input for the ``tags_standard`` field.

    It must be a dict.

    Args:
        data (dict): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, dict):
        raise ValueError(f'Not a  dict ({data})')
    for key in data:
        if not isinstance(key, str) or not isinstance(data[key], str):
            raise ValueError(f'Keys and values must be strings ({key}, {data[key]})')
    return True


def validate_tags_user(data: dict) -> bool:
    """
    Validate input for the ``tags_user`` field.

    It must be a dict.

    Args:
        data (dict): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, dict):
        raise ValueError(f'Not a  dict ({data})')
    for key in data:
        if not isinstance(key, str) or not isinstance(data[key], str):
            raise ValueError(f'Keys and values must be strings ({key}, {data[key]})')
    return True


def validate_title(data: str) -> bool:
    """
    Validate input for the ``title`` field.

    It must be a non-empty string.

    Args:
        data (str): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if validate_string(data) and not data:
        raise ValueError('Must not be empty')
    return True


def validate_url(data: str) -> bool:
    """
    Validate input for a url intended for browsers.

    It must start with ``http(s)://``.

    Args:
        data (str): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, str):
        raise ValueError('Must be a string')
    if not data.startswith('http://') and not data.startswith('https://'):
        raise ValueError('URLs must start with http(s)://')
    return True


def validate_user(data: str) -> bool:
    """
    Validate input for a field containing a single user uuid string.

    All users must exist in the database.

    Args:
        data (str): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, str):
        raise ValueError(f'Bad data type (must be str): {data}')

    try:
        user_uuid = uuid.UUID(data)
    except ValueError as err:
        raise ValueError(f'Not a valid uuid ({data})') from err
    if not flask.g.db['users'].find_one({'_id': user_uuid}):
        raise ValueError(f'Uuid not in db ({data})')
    return True


def validate_user_list(data: Union[str, list]) -> bool:
    """
    Validate input for a field containing a list of user uuid(s).

    For compatibility, the input may be UUIDs as either string (single user) or
    a list (single or multiple users).

    All users must exist in the database.

    Args:
        data (Union[str, list]): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, list):
        raise ValueError(f'Bad data type (must be list): {data}')

    for u_uuid in data:
        try:
            user_uuid = uuid.UUID(u_uuid)
        except ValueError as err:
            raise ValueError(f'Not a valid uuid ({data})') from err
        if not flask.g.db['users'].find_one({'_id': user_uuid}):
            raise ValueError(f'Uuid not in db ({data})')
    return True


VALIDATION_MAPPER = {'affiliation': validate_string,
                     'auth_ids': validate_list_of_strings,
                     'authors': validate_user_list,
                     'contact': validate_string,
                     'description': validate_string,
                     'datasets': validate_datasets,
                     'editors': validate_user_list,
                     'email': validate_email,
                     'generators': validate_user_list,
                     'links': validate_links,
                     'name': validate_string,
                     'orcid': validate_string,
                     'organisation': validate_user,
                     'permissions': validate_permissions,
                     'publications': validate_publications,
                     'tags_standard': validate_tags_std,
                     'tags_user': validate_tags_user,
                     'title': validate_title,
                     'url': validate_url}
