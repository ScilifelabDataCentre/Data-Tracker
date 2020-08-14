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
    return {'_id': utils.new_uuid(),
            'description': '',
            'links': [],
            'title': '',
            'tags_user': []}


def order():
    """
    Provide a basic data structure for an order document.

    Returns:
        dict: The data structure for an order.
    """
    return {'_id': utils.new_uuid(),
            'title': '',
            'description': '',
            'authors': [],
            'generators': [],
            'organisation': '',
            'editors': [],
            'receivers': [],
            'datasets': [],
            'tags_standard': [],
            'tags_user': []}


def project():
    """
    Provide a basic data structure for a project document.

    Returns:
        dict: The data structure for a project.
    """
    return {'_id': utils.new_uuid(),
            'contact': '',
            'datasets': [],
            'description': '',
            'dmp': '',
            'extra': {},
            'owners': [],
            'publications': [],
            'title': ''}


def user():
    """
    Provide a basic data structure for a user document.

    Returns:
        dict: The data structure for a user.
    """
    return {'_id': utils.new_uuid(),
            'affiliation': '',
            'api_key': '',
            'api_salt': '',
            'auth_ids': [],
            'email': '',
            'email_public': '',
            'name': '',
            'orcid': '',
            'permissions': [],
            'url': ''}


def log():
    """
    Provide a basic data structure for a log document.

    Returns:
        dict: The data structure for a log.
    """
    return {'_id': utils.new_uuid(),
            'action': '',
            'comment': '',
            'data_type': '',
            'data': '',
            'timestamp': utils.make_timestamp(),
            'user': ''}
