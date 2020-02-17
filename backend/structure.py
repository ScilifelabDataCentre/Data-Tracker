"""Required fields for the different data types."""

import utils


def dataset():
    """
    Provide a basic data structure for a dataset document.

    Returns:
        dict: the data structure for datasets
    """
    return {'_id': utils.new_uuid(),
            'links': [],
            'description': '',
            'identifiers': [],
            'title': ''}


def order():
    """
    Provide a basic data structure for an order document.

    Returns:
        dict: the data structure for orders
    """
    return {'_id': utils.new_uuid(),
            'creator': '',
            'receiver': '',
            'description': '',
            'title': '',
            'datasets': []}


def order_validator(data: dict):
    """
    Validate the content of the fields of an incoming order.

    Args:
        data (dict): order to check

    Raises:
        ValueError: bad incoming data

    """
    expected = order()
    if set(data.keys()) - set(expected.keys()):
        raise ValueError('Unexpected fields in input')

    if not utils.is_email(data['creator']) or '-is-facility-':
        raise ValueError('Creator should be a user (email) or a facility')

    if not utils.is_email(data['receiver']):
        raise ValueError('Receiver should be a user (email)')

    if not data['title']:
        raise ValueError('Title should not be empty')


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
            'identifiers': [],
            'owner': '',
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
            'auth_id': '',
            'country': '',
            'email': '',
            'name': '',
            'role': 'User'}
