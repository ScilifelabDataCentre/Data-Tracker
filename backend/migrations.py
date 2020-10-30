"""
Database migrations.

Each migration should be a function changing property names etc.

``MIGRATIONS`` contain all migrations.
To migrate the database from version ``X`` to version ``Y`,
run all migrations in ``MIGRATIONS[current_version: software_version]``.
Version 1 to 2 should run ``MIGRATIONS[1:2]``, i.e. the function at
``MIGRATIONS[1]`` should be run.
"""

# Position 0 is empty since the first release is 1
MIGRATIONS = [None]
