"""
Validators for indata.

Indata can be sent to ``validate_field``, which will use the corresponding
functions to check each field.
"""
import re
import uuid
from typing import Any

import flask

import user
import utils


def validate_field(field_key: str, field_value: Any, testing=False) -> bool:
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
        testing (bool): Whether the function is used for testing.

    Returns:
        bool: Whether validation passed.
    """
    try:
        VALIDATION_MAPPER[field_key](field_value)
    except KeyError:
        if not testing:
            flask.current_app.logger.debug("Unknown key: %s", field_key)
        return False
    except ValueError as err:
        if not testing:
            flask.current_app.logger.debug("Indata validation failed: %s - %s", field_key, err)
        return False
    return True


def validate_datasets(data: list, db=None) -> bool:
    """
    Validate input for the ``datasets`` field.

    * It must be a list of strings. 
    * Validate that the datasets exist in the db.

    Args:
        data (str): The data to be validated.
        db: The database to use. Defaults to ``flask.g.db``.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not db:
        db = flask.g.db
    if not isinstance(data, list):
        raise ValueError(f"Must be list ({data})")
    for ds_entry in data:
        if not isinstance(ds_entry, str):
            raise ValueError(f"Must be str ({ds_entry})")
        if not db["datasets"].find_one({"_id": ds_entry}):
            raise ValueError(f"Identifier not in db ({ds_entry})")
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
        raise ValueError(f"Not a string ({data})")
    if data and not utils.is_email(data):
        raise ValueError(f"Not a valid email address ({data})")
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
        raise ValueError(f"Not a list ({data})")
    for entry in data:
        if not isinstance(entry, str):
            raise ValueError(f"Not a string ({entry})")
    return True


def validate_permissions(data: list) -> bool:
    """
    Validate input for the ``permissions`` field.

    * Must be a list containing permissions found in ``PERMISSIONS``
    * Repeats are not allowed

    Args:
        data (list): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, list):
        raise ValueError("Must be a list")
    if len(set(data)) != len(data):
        raise ValueError("Repeats not allowed")
    for entry in data:
        if entry not in user.PERMISSIONS:
            raise ValueError(f"Bad entry ({entry})")
    return True


def validate_string(data: str) -> bool:
    """
    Validate input for a field that must have a ``str`` value.

    Args:
        data (str): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, str):
        raise ValueError(f"Not a string ({data})")
    return True


ORCID_REGEX = re.compile(r"[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}")


def validate_orcid(data: str) -> bool:
    """
    Validate input for the ``orcid`` field.

    * Must be a str
    * Must math xxxx-xxxx-xxxx-xxxx

    Args:
        data (str): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, str):
        raise ValueError(f"Not a str ({data})")
    if data and not ORCID_REGEX.fullmatch(data):
        raise ValueError(f"Not an orcid ({data})")
    return True


def validate_properties(data: dict) -> bool:
    """
    Validate input for the ``properties`` field.

    * Must be a dict
    * Keys and values must be strings
    * Keys and values must be at least 3 characters
    * Keys and values may not end nor start with whitespace

    Args:
        data (dict): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, dict):
        raise ValueError(f"Not a  dict ({data})")
    for key in data:
        if not isinstance(key, str) or not isinstance(data[key], str):
            raise ValueError(f"Keys and values must be strings ({key}, {data[key]})")
        if len(key) < 3 or len(data[key]) < 3:
            raise ValueError("Must be at least three characters")
        if len(key) != len(key.strip()) or len(data[key]) != len(data[key].strip()):
            raise ValueError("May not start nor end with whitespace")
    return True


def validate_tags(data: list) -> bool:
    """
    Validate input for the ``tags`` field.

    * It must be a list
    * Must be at least 3 characters
    * May not end nor start with whitespace

    Args:
        data (list): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not isinstance(data, list):
        raise ValueError(f"Not a list ({data})")
    for value in data:
        if not isinstance(value, str):
            raise ValueError(f"All list entries must be str ({value})")
        if len(value) < 3:
            raise ValueError("Must be at least three characters")
        if len(value) != len(value.strip()):
            raise ValueError("May not start nor end with whitespace")
    return True


def validate_string_non_empty(data: str) -> bool:
    """
    Validate input for string fields that may not be empty.

    It must be a non-empty string.

    Args:
        data (str): The data to be validated.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if validate_string(data) and not data:
        raise ValueError("Must not be empty")
    return True


URL_REGEX = re.compile(r"^https{0,1}://.+")


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
        raise ValueError("Must be a string")
    if data and not URL_REGEX.search(data):
        raise ValueError("URLs must start with http(s)://")
    return True


def validate_user(data: str, db=None) -> bool:
    """
    Validate input for a field containing a single user identifier string.

    All users must exist in the database.

    Args:
        data (str): The data to be validated.
        db: The database to use. Defaults to ``flask.g.db``.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not db:
        db = flask.g.db
    if not isinstance(data, str):
        raise ValueError(f"Bad data type (must be str): {data}")
    if not data:
        return True
    if not db["users"].find_one({"_id": data}):
        raise ValueError(f"Identifier not in db ({data})")
    return True


def validate_user_list(data: list, db=None) -> bool:
    """
    Validate input for a field containing a list of user uuid(s).

    For compatibility, the input may be UUIDs as either string (single user) or
    a list (single or multiple users).

    All users must exist in the database.

    Args:
        data (list): The data to be validated.
        db: The database to use. Defaults to ``flask.g.db``.

    Returns:
        bool: Validation passed.

    Raises:
        ValueError: Validation failed.
    """
    if not db:
        db = flask.g.db
    if not isinstance(data, list):
        raise ValueError(f"Bad data type (must be list): {data}")

    for identifier in data:
        if not isinstance(identifier, str):
            raise ValueError("Bad identifier (should be str)")
        if not db["users"].find_one({"_id": identifier}):
            raise ValueError("Identifier not in db")
    return True


VALIDATION_MAPPER = {
    "affiliation": validate_string,
    "auth_ids": validate_list_of_strings,
    "authors": validate_user_list,
    "contact": validate_string,
    "description": validate_string,
    "datasets": validate_datasets,
    "editors": validate_user_list,
    "email": validate_email,
    "generators": validate_user_list,
    "name": validate_string_non_empty,
    "orcid": validate_orcid,
    "organisation": validate_user,
    "permissions": validate_permissions,
    "properties": validate_properties,
    "tags": validate_tags,
    "title": validate_string_non_empty,
    "url": validate_url,
}
