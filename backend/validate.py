"""
Validators for indata.

Indata can be sent to ``validate_indata``, which will use the corresponding
functions to check each field.
"""
from typing import Any
import logging
import uuid

import flask

import utils


def validate_field(field_key: str, field_value: Any) -> bool:  # pylint: disable=too-many-branches
    """
    Validate that the input data matches expectations.

    Will check the data based on the key name.

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
        if field_key in ('affiliation',
                         'contact',
                         'description'
                         'dmp',
                         'name'):
            validate_string(field_value)
        elif field_key in ('creator', 'receiver'):
            validate_user(field_value, origin=field_key)
        elif field_key == 'datasets':
            validate_datasets(field_value)
        elif field_key == 'email':
            validate_email(field_value)
        elif field_key == 'extra':
            validate_extra(field_value)
        elif field_key == 'links':
            validate_links(field_value)
        elif field_key == 'owners':
            for entry in field_value:
                validate_user(entry, origin=field_key)
        elif field_key == 'publications':
            validate_publications(field_value)
        elif field_key == 'title':
            validate_title(field_value)
        else:
            raise ValueError('Unknown key')
    except ValueError as err:
        logging.info('Indata validation failed: %s - %s', field_key, err)
        return False
    return True


def validate_indata(indata: dict) -> bool:
    """
    Wrapper function to check the fields of a whole dict.

    Args:
        indata (dict): The data to validate.

    Returns:
        bool: Whether validation passed.
    """
    for field_key in indata:
        if not validate_field(field_key, indata[field_key]):
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
            raise ValueError(f'Datasets - not a valid uuid ({data})')
        if not flask.g.db['datasets'].find_one({'_id': ds_uuid}):
            raise ValueError(f'Datasets - uuid not in db ({data})')
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
        raise ValueError(f'Email - not a strin ({data})')
    if not utils.is_email(data):
        raise ValueError(f'Email - not a valid email address ({data})')
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
        raise ValueError(f'Extra - must be dict ({data})')
    for key in data:
        if not isinstance(key, str) or not isinstance(data[key], str):
            raise ValueError(f'Extra - keys and values must be strings ({key}, {data[key]})')
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
        raise ValueError('Links - must be a list')
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError('Links - must be a list of dicts')
        for key in entry:
            if key not in ('url', 'description'):
                raise ValueError('Links - bad key in dict')
            if not isinstance(entry[key], str):
                raise ValueError('Links - values must be type str')
    return True


def validate_publications(data: list) -> bool:
    """
    Validate input for the ``publications`` field.

    It must have the form ``[{'title': value, 'doi': value}, ...]``.

    Args:
        data: The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, list):
        raise ValueError('Publications - must be a list')
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError('Publications - must be a list of dicts')
        for key in entry:
            if key not in ('title', 'doi'):
                raise ValueError('Publications - bad key in dict')
            if not isinstance(entry[key], str):
                raise ValueError('Publications - values must be type str')
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
    validate_string(data)
    if not data:
        raise ValueError('Must not be empty')
    return True


def validate_user(data: str, origin: str) -> bool:
    """
    Validate input for the ``title`` field.

    It must be a non-empty string.
    If uuid, confirms that uuid is present in db.

    Args:
        data (str): The data to be validated.
        origin (str): The key the function was called for.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    # Non-registered user (email instead of uuid)
    if utils.is_email(data):
        return True
    try:
        user_uuid = uuid.UUID(data)
    except ValueError:
        raise ValueError(f'{origin.capitalize()} - not a valid uuid ({data})')
    if not flask.g.db['users'].find_one({'_id': user_uuid}):
        raise ValueError(f'{origin.capitalize()} - uuid not in db ({data})')
    return True
