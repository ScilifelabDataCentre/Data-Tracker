"""
Validators for indata.

Indata can be sent to ``validate_indata``, which will use the corresponding
functions to check each field.
"""
import logging
from typing import Any
import uuid

import utils
import config

def validate_indata(indata: dict) -> bool:  # pylint: disable=too-many-branches
    """
    Validate that the input data matches expectations.

    Will check the indata based on the key names.

    The validation is only done at the technical level,
    e.g. a check that input is of the correct type.

    Checks for e.g. permissions and that the correct fields are provided
    for the entry must be performed separately.

    Args:
        indata (dict): The data to validate.

    Returns:
        bool: Whether validation passed.
    """
    try:
        for field_key in indata:
            if field_key == 'links':
                validate_links(indata[field_key])
            elif field_key == 'title':
                validate_title(indata[field_key])
            elif field_key == 'description':
                validate_description(indata[field_key])
            elif field_key == 'extra':
                validate_extra(indata[field_key])
            elif field_key in ('creator', 'receiver'):
                validate_user(indata[field_key], origin=field_key)
            else:
                raise ValueError('Unknown key')
    except ValueError as err:
        logging.info('Indata validation failed: %s', err)
        return False
    return True


def validate_description(data) -> bool:
    """
    Validate input for the ``description`` field.

    It must be a string.

    Args:
        data: The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, str):
        raise ValueError(f'Description - not a string ({data})')
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
        raise ValueError('Links- must be a list')
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError('Links - list must contain dicts')
        for key in entry:
            if key not in ('url', 'description'):
                raise ValueError('Links - bad key in dict')
            if not isinstance(entry[key], str):
                raise ValueError('Links - values must be type str')

    return True


def validate_title(data) -> bool:
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
    if not isinstance(data, str):
        raise ValueError('Title - not a string')
    if not data:
        raise ValueError('Title - must be non-empty')
    return True


def validate_user(data: str, origin: str) -> bool:
    """
    Validate input for the ``title`` field.

    It must be a non-empty string.

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
    return True
