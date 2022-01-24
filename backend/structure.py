"""
Required fields for the different data types.

See documentation (Data Structure) for more information.
"""

import utils


def dataset():
    """
    Provide a basic data structure for a dataset document.

    Returns:
        dict: The data structure for a dataset.
    """
    return {
        "_id": "d-" + utils.new_uuid(),
        "description": "",
        "title": "",
        "properties": {},
        "tags": [],
    }


def order():
    """
    Provide a basic data structure for an order document.

    Returns:
        dict: The data structure for an order.
    """
    return {
        "_id": "o-" + utils.new_uuid(),
        "title": "",
        "description": "",
        "authors": [],
        "generators": [],
        "organisation": {},
        "editors": [],
        "datasets": [],
        "properties": {},
        "tags": [],
    }


def collection():
    """
    Provide a basic data structure for a project document.

    Returns:
        dict: The data structure for a project.
    """
    return {
        "_id": "c-" + utils.new_uuid(),
        "datasets": [],
        "description": "",
        "properties": {},
        "tags": [],
        "editors": [],
        "title": "",
    }


def user():
    """
    Provide a basic data structure for a user document.

    Returns:
        dict: The data structure for a user.
    """
    return {
        "_id": "u-" + utils.new_uuid(),
        "affiliation": "",
        "api_key": "",
        "api_salt": "",
        "auth_ids": [],
        "email": "",
        "contact": "",
        "name": "",
        "orcid": "",
        "permissions": [],
        "url": "",
    }


def team():
    """
    Provide a basic data structure for a team document.

    Returns:
        dict: The data structure for a team.
    """
    return {
        "_id": "t-" + utils.new_uuid(),
        "affiliation": "",
        "email": "",
        "contact": "",
        "name": "",
        "url": "",
        "members": [],
        "admins": [],
    }


def log():
    """
    Provide a basic data structure for a log document.

    Returns:
        dict: The data structure for a log.
    """
    return {
        "_id": "l-" + utils.new_uuid(),
        "action": "",
        "comment": "",
        "data_type": "",
        "data": "",
        "timestamp": utils.make_timestamp(),
        "user": "",
    }
