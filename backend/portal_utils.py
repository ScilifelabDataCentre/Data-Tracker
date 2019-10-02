"""
Helper functions
"""
import db
import portal_errors


def get_dataset(ds_id: int, user) -> dict:
    """
    Retrieve a complete dataset from database, with permission checks.

    Args:
        ds_id (int): The database id of the dataset
        user: The current user

    Returns:
        dict: The complete dataset, including e.g. tags

    Raises:
        db.Dataset.DoesNotExist: No dataset with id ds_id exists in the db
        portal_errors.InsufficientPermissions: Current user does not have the required permissions

    """
    dataset = db.Dataset.get_by_id(ds_id)

    if not dataset.visible and not (has_rights(user, ('Steward', 'Admin'))
                                    or is_owner(user, dataset)):
        raise portal_errors.InsufficientPermissions("Dataset not available for the current user.")

    dataset = db.build_dict_from_row(dataset)
    dataset['tags'] = [entry for entry in (db.DatasetTag
                                           .select(db.Tag)
                                           .join(db.Tag)
                                           .where(db.DatasetTag.dataset == ds_id)
                                           .dicts())]

    dataset['publications'] = [entry for entry in (db.DatasetPublication
                                                   .select(db.Publication)
                                                   .join(db.Publication)
                                                   .where(db.DatasetPublication.dataset == ds_id)
                                                   .dicts())]

    dataset['data_urls'] = [entry for entry in (db.DatasetDataUrl
                                                .select(db.DataUrl)
                                                .join(db.DataUrl)
                                                .where(db.DatasetDataUrl.dataset == ds_id)
                                                .dicts())]

    dataset['owners'] = [entry for entry in (db.DatasetOwner
                                             .select(db.User.name)
                                             .join(db.User)
                                             .where(db.DatasetOwner.dataset == ds_id)
                                             .dicts())]

    return dataset


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
