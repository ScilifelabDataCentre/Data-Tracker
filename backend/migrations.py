"""
Database migrations.

Each migration should be a function changing property names etc.

``MIGRATIONS`` contain all migrations.
To migrate the database from version ``X`` to version ``Y`,
run all migrations in ``MIGRATIONS[current_version: software_version]``.
Version 1 to 2 should run ``MIGRATIONS[1:2]``, i.e. the function at
``MIGRATIONS[1]`` should be run.
"""

import logging


def migrate_v1_to_v2(db):
    """
    Update the database fields to match the changes in the data structure.

    * Rename all ``ORDERS`` permissions to ``DATA_EDIT`` to match the updated permission names
    * Remove the ``cross_references`` field from collections and datasets
    """
    logging.info("Renaming ORDERS to DATA_EDIT")
    db["users"].update_many({"permissions": "ORDERS"}, {"$push": {"permissions": "DATA_EDIT"}})
    db["users"].update_many({"permissions": "ORDERS"}, {"$pull": {"permissions": "ORDERS"}})
    logging.info("Removing the cross_references field")
    db["collections"].update_many({}, {"$unset": {"cross_references": ""}})
    db["datasets"].update_many({}, {"$unset": {"cross_references": ""}})


def migrate_v2_to_v3(db):
    """
    Update the database fields to match the changes in the data structure.

    * Remove the ``DATA_LIST`` and ``STATISTICS`` permissions from all users.
    """
    logging.info("Remove the DATA_LIST and STATISTICS permissions")
    db["users"].update_many({}, {"$pull": {"permissions": {$in: ["STATISTICS", "DATA_LIST"]}}})


# Position 0 is empty since the first release is 1
MIGRATIONS = [None, migrate_v1_to_v2, migrate_v2_to_v3]
