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
    logging.info("Orders - update identifiers to new format")
    entries = list(db["orders"].find({}))
    if entries:
        for entry in entries:
            if str(entry["_id"]).startswith("o-"):
                continue
            entry["_id"] = "o-" + str(entry["_id"])
            entry["authors"] = ["u-" + str(uentry) for uentry in entry["authors"]]
            entry["generators"] = ["u-" + str(uentry) for uentry in entry["generators"]]
            entry["organisation"] = "u-" + str(entry["organisation"])
            entry["editors"] = ["u-" + str(uentry) for uentry in entry["editors"]]
            entry["datasets"] = ["d-" + str(dentry) for dentry in entry["datasets"]]
        db["orders"].delete_many({})
        db["orders"].insert_many(entries)

    logging.info("Datasets - update identifiers to new format")
    entries = list(db["datasets"].find({}))
    if entries:
        for entry in entries:
            if str(entry["_id"]).startswith("d-"):
                continue
            entry["_id"] = "d-" + str(entry["_id"])
        db["datasets"].delete_many({})
        db["datasets"].insert_many(entries)

    logging.info("Collections - update identifiers to new format")
    entries = list(db["collections"].find({}))
    if entries:
        for entry in entries:
            if str(entry["_id"]).startswith("c-"):
                continue
            entry["_id"] = "c-" + str(entry["_id"])
            entry["editors"] = ["u-" + str(uentry) for uentry in entry["editors"]]
            entry["datasets"] = ["d-" + str(dentry) for dentry in entry["datasets"]]
        db["collections"].delete_many({})
        db["collections"].insert_many(entries)

    logging.info("Collections - update identifiers to new format")
    entries = list(db["collections"].find({}))
    if entries:
        for entry in entries:
            if str(entry["_id"]).startswith("c-"):
                continue
            entry["_id"] = "c-" + str(entry["_id"])
        db["collections"].delete_many({})
        db["collections"].insert_many(entries)

    logging.info("Add prefix to users")
    entries = list(db["users"].find({}))
    if entries:
        for entry in entries:
            entry["_id"] = "u-" + str(entry["_id"])
        db["users"].delete_many({})
        db["users"].insert_many(entries)

    logging.info("Add prefix to logs")
    entries = list(db["logs"].find({}))
    if entries:
        for entry in entries:
            if str(entry["_id"]).startswith("l-"):
                continue
            entry["_id"] = "l-" + str(entry["_id"])
            if entry["data_type"] == "dataset":
                entry["data"]["_id"] = "d-" + str(entry["_id"])
            elif entry["data_type"] == "order":
                entry["data"]["_id"] = "o-" + str(entry["_id"])
                if entry["action"] != 'delete':
                    entry["data"]["authors"] = [
                        "u-" + str(uentry) for uentry in entry["data"]["authors"]
                    ]
                    entry["data"]["generators"] = [
                        "u-" + str(uentry) for uentry in entry["data"]["generators"]
                    ]
                    entry["data"]["organisation"] = "u-" + str(entry["data"]["organisation"])
                    entry["data"]["editors"] = [
                        "u-" + str(uentry) for uentry in entry["data"]["editors"]
                    ]
                    entry["data"]["datasets"] = [
                        "d-" + str(dentry) for dentry in entry["data"]["datasets"]
                    ]
            elif entry["data_type"] == "collection":
                if entry["action"] != 'delete':
                    entry["data"]["_id"] = "o-" + str(entry["_id"])
                    entry["data"]["editors"] = [
                        "u-" + str(uentry) for uentry in entry["data"]["editors"]
                    ]
                    entry["data"]["datasets"] = [
                        "d-" + str(dentry) for dentry in entry["data"]["datasets"]
                    ]
            elif entry["data_type"] == "user":
                entry["data"]["_id"] = "u-" + str(entry["_id"])
        db["logs"].delete_many({})
        db["logs"].insert_many(entries)


# Position 0 is empty since the first release is 1
MIGRATIONS = [None, migrate_v1_to_v2, migrate_v2_to_v3, migrate_v3_to_v4]
