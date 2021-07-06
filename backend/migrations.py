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
    db["users"].update_many({}, {"$pull": {"permissions": {"$in": ["STATISTICS", "DATA_LIST"]}}})


def migrate_v3_to_v4(db):
    """
    Add prefixes to all _id fields.

    * Add o- to orders
    * Add d- to datasets
    * Add c- to collections
    * Add u- to users
    * Add l- to logs
    """
    logging.info("Add prefix to orders")
    entries = list(db["orders"].find({}))
    if entries:
        for entry in entries:
            entry['_id'] = 'o-' + str(entry['_id'])
        db["orders"].delete_many({})
        db["orders"].insert_many(entries)
    
    logging.info("Add prefix to datasets")
    entries = list(db["datasets"].find({}))
    if entries:
        for entry in entries:
            entry['_id'] = 'd-' + str(entry['_id'])
        db["datasets"].delete_many({})
        db["datasets"].insert_many(entries)

    logging.info("Add prefix to collections")
    entries = list(db["collections"].find({}))
    if entries:
        for entry in entries:
            entry['_id'] = 'c-' + str(entry['_id'])
        db["collections"].delete_many({})
        db["collections"].insert_many(entries)

    logging.info("Add prefix to users")
    entries = list(db["users"].find({}))
    if entries:
        for entry in entries:
            entry['_id'] = 'u-' + str(entry['_id'])
        db["users"].delete_many({})
        db["users"].insert_many(entries)

    logging.info("Add prefix to logs")
    entries = list(db["logs"].find({}))
    if entries:
        for entry in entries:
            entry['_id'] = 'l-' + str(entry['_id'])
        db["logs"].delete_many({})
        db["logs"].insert_many(entries)
    

# Position 0 is empty since the first release is 1
MIGRATIONS = [None, migrate_v1_to_v2, migrate_v2_to_v3, migrate_v3_to_v4]
