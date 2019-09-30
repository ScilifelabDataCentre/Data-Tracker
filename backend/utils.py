"""
Helper functions
"""
import db


def has_rights(user, permissions: tuple) -> bool:
    """
    Test whether the user has the supplied permissions.

    Args:
        user: user to test
        permissions (tuple): permissions of interest

    Returns:
        bool: whether user has Admin rights

    """
    try:
        if user.permission in permissions:
            return True
    except AttributeError:
        pass
    return False


def is_owner(user, dataset) -> bool:
    """
    Test whether the user owns the provided dataset

    Args:
        user: the user to test
        dataset: the dataset to check owners for

    Returns:
        bool: whether user owns the dataset

    """
    try:
        db.DatasetOwner.get((db.DatasetOwner.dataset == dataset.id) &
                            (db.DatasetOwner.user == user))
        return True
    except db.DatasetOwner.DoesNotExist:
        return False
