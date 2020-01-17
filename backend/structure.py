"""Required fields for the different data types."""

import datetime

import utils


def user():
    """
    Provide a basic data structure for a user.

    Returns:
        dict: the data structure for users
    """
    return {'affiliation': '',
            'auth_id': '',
            'country': '',
            'email': '',
            'name': '',
            'role': 'User',
            'timestamp': datetime.datetime.now()}


def dataset():
    """
    Provide a basic data structure for a dataset.

    Returns:
        dict: the data structure for datasets
    """
    return {'creator': '',
            'data_urls': [],
            'description': '',
            'dmp': '',
            'identifier': '',
            'publications': [],
            'timestamp': datetime.datetime.now(),
            'title': '',
            'uuid': utils.new_uuid()}


def project():
    """
    Provide a basic data structure for a project.

    Returns:
        dict: the data structure for projects
    """
    return {'contact': '',
            'description': '',
            'identifier': '',
            'owner': '',
            'timestamp': datetime.datetime.now(),
            'title': '',
            'datasets': [],
            'uuid': utils.new_uuid()}
