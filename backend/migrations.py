"""
Database migrations.

Each migration should be a function changing property names etc.

``MIGRATIONS`` contain all migrations.
To migrate the database from version ``X`` to version ``Y`,
run all migrations in ``MIGRATIONS[current_version: software_version]``.
Version 1 to 2 should run ``MIGRATIONS[1:2]``, i.e. the function at
``MIGRATIONS[1]`` should be run.
"""

def migrate_v1_to_v2(db):
    """Rename all ORDERS permissions to DATA_EDIT to match the updated permission names."""
    db["users"].update_many({"permissions": "ORDERS"}, {"$push": {"permissions": "DATA_EDIT"}})
    db["users"].update_many({"permissions": "ORDERS"}, {"$pull": {"permissions": "ORDERS"}})

# Position 0 is empty since the first release is 1
MIGRATIONS = [None, migrate_v1_to_v2]
