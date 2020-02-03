"""Required fields for the different data types."""

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
            'role': 'User'}


def dataset():
    """
    Provide a basic data structure for a dataset.

    Returns:
        dict: the data structure for datasets
    """
    return {'data_urls': [],
            'description': '',
            'identifier': '',
            'title': '',
            '_id': utils.new_uuid()}


def order():
    """
    Provide a basic data structure for an order.

    Returns:
        dict: the data structure for orders
    """
    return {'creator': '',
            'receiver': '',
            'description': '',
            'title': '',
            '_id': utils.new_uuid()}


def order_validator(order: dict):
    """
    Validate the content of the fields of an incoming order.

    Args:
        order (dict): order to check

    Raises:
        ValueError: bad incoming data

    """
    expected = order()
    if set(in_order.keys()) - set(expected.keys()):
        raise ValueError('Unexpected fields in input')

    if not utils.is_email(in_order['creator']) or '-is-facility-':
        raise ValueError('Creator should be a user (email) or a facility')

    if not utils.is_email(in_order['receiver']):
        raise ValueError('Receiver should be a user (email)')

    if not title:
        raise ValueError('Title should not be empty')


def project():
    """
    Provide a basic data structure for a project.

    Returns:
        dict: the data structure for projects
    """
    return {'dmp': '',
            'contact': '',
            'description': '',
            'identifier': '',
            'owner': '',
            'publications': [],
            'title': '',
            'datasets': [],
            '_id': utils.new_uuid()}
