"""
Helper functions
"""
import db
import portal_errors


def get_dataset(ds_id: int, user) -> dict:
    """
    Retrieve a complete dataset.
    Args:
        ds_id (int): The database id of the dataset
        user: The current user

    Returns:
        dict: The complete dataset, including e.g. tags

    Raises:
        db.Dataset.DoesNotExist: No dataset with id ds_id exists in the db
        portal_errors.InsufficientPermissions: Current user does not have the required permissions

    """
    dataset = (db.Dataset
               .select()
               .where(db.Dataset.id == ds_id)
               .dicts()
               .get())

    dataset['tags'] = list(db.DatasetTag
                           .select(db.Tag)
                           .join(db.Tag)
                           .where(db.DatasetTag.dataset == ds_id)
                           .dicts())

    dataset['publications'] = list(db.DatasetPublication
                                   .select(db.Publication)
                                   .join(db.Publication)
                                   .where(db.DatasetPublication.dataset == ds_id)
                                   .dicts())

    dataset['data_urls'] = list(db.DatasetDataUrl
                                .select(db.DataUrl)
                                .join(db.DataUrl)
                                .where(db.DatasetDataUrl.dataset == ds_id)
                                .dicts())

    return dataset


def has_rights(user, permissions: tuple) -> bool:
    """
    Test whether the user has the supplied permissions.

    Args:
        user (User): user to test
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
        user (db.User): the user to test
        dataset (db.Dataset): the dataset to check owners for

    Returns:
        bool: whether user owns the dataset

    """
    query = (db.ProjectOwner
             .select(db.ProjectOwner.project)
             .join(db.ProjectDataset, on=(db.ProjectOwner.project == db.ProjectDataset.project))
             .where((db.ProjectDataset.dataset == dataset.id) &
                    (db.ProjectOwner.user == user)))
    return bool(list(query))
