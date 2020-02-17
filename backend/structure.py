"""
Required fields for the different data types.

See documentation (Data Structure) for more information.
"""

import utils


def dataset():
    """
    Provide a basic data structure for a dataset document.

    Returns:
        dict: the data structure for datasets
    """
    return {'_id': utils.new_uuid(),
            'description': '',
            'extra': [],
            'links': [],
            'title': ''}


def order():
    """
    Provide a basic data structure for an order document.

    Returns:
        dict: the data structure for orders
    """
    return {'_id': utils.new_uuid(),
            'creator': '',
            'datasets': [],
            'description': '',
            'extra': [],
            'receiver': '',
            'title': ''}


def project():
    """
    Provide a basic data structure for a project document.

    Returns:
        dict: the data structure for projects
    """
    return {'_id': utils.new_uuid(),
            'contact': '',
            'datasets': [],
            'description': '',
            'dmp': '',
            'extra': [],
            'owners': [],
            'publications': [],
            'title': ''}


def user():
    """
    Provide a basic data structure for a user document.

    Returns:
        dict: the data structure for users
    """
    return {'_id': utils.new_uuid(),
            'affiliation': '',
            'api_key': '',
            'auth_id': '',
            'country': '',
            'email': '',
            'name': '',
            'permissions': []}
